"""Bridge normalized catalog cases into legacy ``cases`` rows for Rack Builder.

Racks still bind to the legacy ``cases`` table via ``case_id``. This helper
creates or reuses a placement-compatible legacy row from a catalog revision
without inventing unspecified rails or depths.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from cases.catalog_service import get_case_by_slug, pick_primary_revision
from cases.models import Case, CaseCatalog, CasePowerSystem, CaseRevision, CaseRow


def _legacy_format_label(format_family: str) -> str:
    """Map catalog enums to the human labels used by legacy filters."""
    mapping = {
        "eurorack": "Eurorack",
        "intellijel_1u": "Eurorack",
        "pulplogic_1u": "Eurorack",
        "buchla_200": "Buchla",
        "serge_4u": "Serge 4U",
        "mu_5u": "5U MU",
        "frac": "Frac",
        "other": "Other",
    }
    return mapping.get(format_family, format_family)


def _legacy_capacity_unit(unit: Optional[str]) -> str:
    if not unit or unit == "hp":
        return "hp"
    # Legacy research used plural-ish names; keep catalog unit when non-HP.
    return unit


def _row_hp_layout(revision: CaseRevision, case: CaseCatalog) -> tuple[int, list[int]]:
    rows = sorted(list(revision.rows or []), key=lambda r: r.row_index)
    if rows and all(r.capacity_value is not None for r in rows):
        hp_per_row = [int(r.capacity_value or 0) for r in rows]
        # Guard zero/negative for legacy Case.total_hp > 0 constraint.
        if all(v > 0 for v in hp_per_row):
            return len(hp_per_row), hp_per_row

    if revision.capacity_value is not None and revision.capacity_value > 0:
        count = max(int(revision.row_count or 1), 1)
        total = int(revision.capacity_value)
        if count == 1:
            return 1, [total]
        # Even split when possible; remainder on last row.
        base = total // count
        rem = total - base * count
        if base <= 0:
            return 1, [total]
        layout = [base] * count
        layout[-1] += rem
        return count, layout

    # Fail-closed minimum valid layout for identity-only records.
    return 1, [1]


def _primary_power(revision: CaseRevision) -> Optional[CasePowerSystem]:
    systems = list(revision.power_systems or [])
    if not systems:
        return None
    for s in systems:
        if s.name == "primary":
            return s
    return systems[0]


def _meta_payload(
    catalog: CaseCatalog,
    revision: CaseRevision,
    *,
    existing_meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    meta: dict[str, Any] = dict(existing_meta or {})
    meta.update(
        {
            "catalog_slug": catalog.slug,
            "catalog_format_family": catalog.format_family,
            "catalog_revision_key": revision.revision_key,
            "format_family": _legacy_format_label(catalog.format_family),
            "capacity_unit": revision.capacity_unit or "hp",
            "powered": catalog.powered,
            "source": "case_catalog",
        }
    )
    if revision.depth_min_mm is not None:
        meta["depth_min_mm"] = revision.depth_min_mm
    if revision.depth_max_mm is not None:
        meta["depth_max_mm"] = revision.depth_max_mm
    if revision.depth_notes:
        meta["depth_notes"] = revision.depth_notes
    if revision.mounting_type:
        meta["mounting"] = revision.mounting_type
    if revision.confidence:
        meta["catalog_confidence"] = revision.confidence
    return meta


def materialize_legacy_case(
    db: Session,
    slug: str,
    *,
    revision_key: Optional[str] = None,
) -> tuple[Case, bool]:
    """Return ``(legacy_case, created)`` for the catalog slug.

    Idempotent: reuses an existing legacy row tagged with ``meta.catalog_slug``
    or matching manufacturer/model from catalog materialization.
    """
    catalog = get_case_by_slug(db, slug)
    if catalog is None:
        raise LookupError(f"Catalog case not found: {slug}")

    if revision_key:
        revision = next((r for r in catalog.revisions if r.revision_key == revision_key), None)
        if revision is None:
            raise LookupError(f"Revision not found: {revision_key}")
    else:
        revision = pick_primary_revision(list(catalog.revisions or []))
        if revision is None:
            raise LookupError("Case has no revisions")

    # Prefer exact catalog_slug match in meta JSON (SQLite/Postgres both support as_string path via Python filter).
    candidates = (
        db.query(Case)
        .filter(Case.brand == catalog.manufacturer, Case.name == catalog.model)
        .all()
    )
    existing: Optional[Case] = None
    for row in candidates:
        meta = row.meta if isinstance(row.meta, dict) else {}
        if meta.get("catalog_slug") == catalog.slug:
            existing = row
            break
    if existing is None:
        # Also accept prior ResearchCSV rows with same brand/name.
        for row in candidates:
            meta = row.meta if isinstance(row.meta, dict) else {}
            if meta.get("catalog_slug") in (None, catalog.slug):
                existing = row
                break

    rows_count, hp_per_row = _row_hp_layout(revision, catalog)
    total_hp = sum(hp_per_row)
    power = _primary_power(revision)
    unit = _legacy_capacity_unit(revision.capacity_unit)
    family = _legacy_format_label(catalog.format_family)
    notes = revision.notes or f"{catalog.manufacturer} {catalog.model} (catalog)"

    if existing is None:
        legacy = Case(
            brand=catalog.manufacturer,
            name=catalog.model,
            total_hp=total_hp,
            rows=rows_count,
            hp_per_row=hp_per_row,
            format_family=family,
            capacity_unit=unit,
            powered=catalog.powered,
            power_12v_ma=power.current_pos12_ma if power else None,
            power_neg12v_ma=power.current_neg12_ma if power else None,
            power_5v_ma=power.current_pos5_ma if power else None,
            description=notes[:2000] if notes else None,
            manufacturer_url=catalog.official_url,
            meta=_meta_payload(catalog, revision),
            source="case_catalog",
            source_reference=f"catalog:{catalog.slug}:{revision.revision_key}",
        )
        db.add(legacy)
        db.commit()
        db.refresh(legacy)
        return legacy, True

    # Refresh placement-critical fields from catalog (null-preserving for rails).
    existing.total_hp = total_hp
    existing.rows = rows_count
    existing.hp_per_row = hp_per_row
    existing.format_family = family
    existing.capacity_unit = unit
    existing.powered = catalog.powered
    if power:
        existing.power_12v_ma = power.current_pos12_ma
        existing.power_neg12v_ma = power.current_neg12_ma
        existing.power_5v_ma = power.current_pos5_ma
    existing.description = notes[:2000] if notes else existing.description
    existing.manufacturer_url = catalog.official_url or existing.manufacturer_url
    existing.meta = _meta_payload(
        catalog, revision, existing_meta=existing.meta if isinstance(existing.meta, dict) else {}
    )
    existing.source = "case_catalog"
    existing.source_reference = f"catalog:{catalog.slug}:{revision.revision_key}"
    db.add(existing)
    db.commit()
    db.refresh(existing)
    return existing, False
