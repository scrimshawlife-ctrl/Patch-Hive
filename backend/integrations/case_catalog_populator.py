"""Deterministic JSON importer for the normalized modular case catalog.

The importer is intentionally strict: missing values remain ``None`` and are
never inferred. Every run emits a receipt with the input SHA-256 and row counts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from cases.models import (
    CaseCatalog,
    CaseFeature,
    CasePowerSystem,
    CasePrice,
    CaseRevision,
    CaseRow,
    CaseSource,
)
from core.database import SessionLocal

FORMAT_FAMILIES = {
    "eurorack",
    "intellijel_1u",
    "pulplogic_1u",
    "buchla_200",
    "serge_4u",
    "mu_5u",
    "frac",
    "other",
}
CAPACITY_UNITS = {"hp", "mu_space", "buchla_panel", "serge_panel", "frac_width", "custom"}
CONFIDENCE = {"verified", "high", "medium", "low", "conflict"}


def _valid_url(value: str | None) -> bool:
    if not value:
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_record(record: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    for field in ("manufacturer", "model", "format_family"):
        if not str(record.get(field, "")).strip():
            errors.append(f"record[{index}].{field}: required")
    if record.get("format_family") not in FORMAT_FAMILIES:
        errors.append(f"record[{index}].format_family: unsupported value")
    for field in ("official_url", "image_url"):
        if not _valid_url(record.get(field)):
            errors.append(f"record[{index}].{field}: invalid URL")

    revision = record.get("revision") or {}
    unit = revision.get("capacity_unit")
    if unit is not None and unit not in CAPACITY_UNITS:
        errors.append(f"record[{index}].revision.capacity_unit: unsupported value")
    confidence = revision.get("confidence", "medium")
    if confidence not in CONFIDENCE:
        errors.append(f"record[{index}].revision.confidence: unsupported value")

    for source_index, source in enumerate(record.get("sources") or []):
        if not _valid_url(source.get("url")):
            errors.append(f"record[{index}].sources[{source_index}].url: invalid URL")
        if source.get("confidence", "medium") not in CONFIDENCE:
            errors.append(f"record[{index}].sources[{source_index}].confidence: unsupported value")
    return errors


def import_records(db: Session, records: list[dict[str, Any]], dry_run: bool = False) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "status": "success",
        "input_records": len(records),
        "inserted": 0,
        "updated": 0,
        "rejected": 0,
        "warnings": [],
    }

    for index, record in enumerate(records):
        errors = validate_record(record, index)
        if errors:
            receipt["rejected"] += 1
            receipt["warnings"].extend(errors)
            continue

        manufacturer = record["manufacturer"].strip()
        model = record["model"].strip()
        slug = record.get("slug") or CaseCatalog.create_slug(manufacturer, model)
        case = db.query(CaseCatalog).filter(CaseCatalog.slug == slug).first()
        created = case is None
        if created:
            case = CaseCatalog(slug=slug, manufacturer=manufacturer, model=model, format_family=record["format_family"])
            db.add(case)
            db.flush()
        case.manufacturer = manufacturer
        case.model = model
        case.format_family = record["format_family"]
        case.production_status = record.get("production_status", "unknown")
        case.powered = record.get("powered")
        case.image_url = record.get("image_url")
        case.official_url = record.get("official_url")

        revision_data = record.get("revision") or {}
        revision_key = revision_data.get("revision_key", "default")
        revision = (
            db.query(CaseRevision)
            .filter(CaseRevision.case_id == case.id, CaseRevision.revision_key == revision_key)
            .first()
        )
        if revision is None:
            revision = CaseRevision(case_id=case.id, revision_key=revision_key)
            db.add(revision)
            db.flush()
        for field in (
            "revision_label", "row_count", "capacity_value", "capacity_unit", "usable_capacity_value",
            "depth_min_mm", "depth_max_mm", "depth_notes", "width_mm", "height_mm", "depth_mm",
            "weight_kg", "materials", "mounting_type", "portable", "removable_lid",
            "close_patched_lid", "integrated_stand", "rack_mountable", "notes", "confidence",
        ):
            if field in revision_data:
                setattr(revision, field, revision_data[field])

        for row_data in record.get("rows") or []:
            row = (
                db.query(CaseRow)
                .filter(CaseRow.revision_id == revision.id, CaseRow.row_index == row_data["row_index"])
                .first()
            ) or CaseRow(revision_id=revision.id, row_index=row_data["row_index"], format_family=row_data.get("format_family", case.format_family))
            db.add(row)
            for field in ("format_family", "capacity_value", "capacity_unit", "usable_capacity_value", "depth_min_mm", "depth_max_mm", "notes"):
                if field in row_data:
                    setattr(row, field, row_data[field])

        for power_data in record.get("power_systems") or []:
            name = power_data.get("name", "primary")
            power = (
                db.query(CasePowerSystem)
                .filter(CasePowerSystem.revision_id == revision.id, CasePowerSystem.name == name)
                .first()
            ) or CasePowerSystem(revision_id=revision.id, name=name)
            db.add(power)
            for field in ("supply_type", "external_input", "busboard_type", "connector_count", "current_pos12_ma", "current_neg12_ma", "current_pos5_ma", "power_watts", "zoned_distribution", "protections", "notes"):
                if field in power_data:
                    setattr(power, field, power_data[field])

        for feature_data in record.get("features") or []:
            key = feature_data["feature_key"]
            feature = (
                db.query(CaseFeature)
                .filter(CaseFeature.revision_id == revision.id, CaseFeature.feature_key == key)
                .first()
            ) or CaseFeature(revision_id=revision.id, feature_key=key)
            db.add(feature)
            feature.feature_value = feature_data.get("feature_value")
            feature.verified = feature_data.get("verified", False)

        for source_data in record.get("sources") or []:
            field_path = source_data.get("field_path")
            source = (
                db.query(CaseSource)
                .filter(CaseSource.case_id == case.id, CaseSource.url == source_data["url"], CaseSource.field_path == field_path)
                .first()
            ) or CaseSource(case_id=case.id, revision_id=revision.id, url=source_data["url"], field_path=field_path, source_type=source_data["source_type"])
            db.add(source)
            for field in ("revision_id", "source_type", "title", "published_value", "normalized_value", "discrepancy_note", "confidence"):
                if field in source_data:
                    setattr(source, field, source_data[field])

        for price_data in record.get("prices") or []:
            db.add(CasePrice(case_id=case.id, **price_data))

        receipt["inserted" if created else "updated"] += 1

    if dry_run:
        db.rollback()
    else:
        db.commit()
    return receipt


def run(path: Path, dry_run: bool = False) -> dict[str, Any]:
    raw = path.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    records = payload["cases"] if isinstance(payload, dict) else payload
    db = SessionLocal()
    try:
        receipt = import_records(db, records, dry_run=dry_run)
        receipt["input_sha256"] = hashlib.sha256(raw).hexdigest()
        receipt["input_path"] = str(path)
        receipt["dry_run"] = dry_run
        return receipt
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate the PatchHive modular case catalog")
    parser.add_argument("--input", required=True, type=Path, help="JSON dataset path")
    parser.add_argument("--dry-run", action="store_true", help="Validate and roll back all writes")
    parser.add_argument("--receipt", type=Path, help="Optional JSON receipt output path")
    args = parser.parse_args()
    receipt = run(args.input, dry_run=args.dry_run)
    rendered = json.dumps(receipt, indent=2, sort_keys=True)
    print(rendered)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(rendered + "\n", encoding="utf-8")
    if receipt["rejected"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
