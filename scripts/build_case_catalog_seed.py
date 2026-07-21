#!/usr/bin/env python3
"""Convert Cases4PatchHive research fixture into canonical case-catalog seed JSON.

Outputs:
  data/cases/seed-v1.json
  data/cases/seed-v1.sources.json
  data/cases/seed-v1.coverage.json

Rules:
  - Unknown / unspecified values become null (never 0/false/empty-string defaults).
  - Format families and capacity units use the catalog enums.
  - Field-level source records + policy packets accompany non-null technical fields.
  - Research synthesis is not treated as manufacturer-verified canonical truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESEARCH = REPO_ROOT / "fixtures" / "cases_research_2026.json"
DEFAULT_MD = REPO_ROOT / "fixtures" / "Cases4PatchHive.md"
DEFAULT_SEED = REPO_ROOT / "data" / "cases" / "seed-v1.json"
DEFAULT_SOURCES = REPO_ROOT / "data" / "cases" / "seed-v1.sources.json"
DEFAULT_COVERAGE = REPO_ROOT / "data" / "cases" / "seed-v1.coverage.json"

NORMALIZER_VERSION = "case-catalog-v1"
DATASET_VERSION = "case-catalog-seed-v1"
OBSERVED_AT = "2026-07-21T00:00:00Z"
RETRIEVED_AT = "2026-07-21T12:00:00Z"
# Fixed stamp so rebuilds are SHA-stable (do not use wall-clock time).
GENERATED_AT = "2026-07-21T20:24:00Z"
RESEARCH_SOURCE_URL = (
    "https://github.com/scrimshawlife-ctrl/Patch-Hive/blob/main/fixtures/Cases4PatchHive.md"
)
RESEARCH_SOURCE_TITLE = "Cases4PatchHive research master table (2026)"

FORMAT_MAP = {
    "eurorack": "eurorack",
    "buchla": "buchla_200",
    "serge 4u": "serge_4u",
    "5u mu": "mu_5u",
    "frac": "frac",
}

UNIT_MAP = {
    "hp": "hp",
    "buchla_panels": "buchla_panel",
    "mu_spaces": "mu_space",
    "serge_panels": "serge_panel",
    "serge_4x4_modules": "serge_panel",
    "frac_widths": "frac_width",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _unspecified(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    v = value.strip().lower()
    return v in {"", "unspecified", "n/a", "none", "unknown"}


def _to_mm(number: float, unit: str) -> float:
    u = unit.lower()
    if u in {"mm", "millimeter", "millimetre"}:
        return round(number, 3)
    if u in {'"', "in", "inch", "inches"}:
        return round(number * 25.4, 3)
    if u == "cm":
        return round(number * 10.0, 3)
    raise ValueError(f"unsupported length unit: {unit}")


def _parse_fractional_inches(token: str) -> float | None:
    """Parse 2, 2.5, 3 3/8, 3/8."""
    t = token.strip().lower().replace("″", '"').replace("”", '"')
    t = re.sub(r'(in|inch|inches|")$', "", t).strip()
    m = re.fullmatch(r"(\d+)\s+(\d+)/(\d+)", t)
    if m:
        return int(m.group(1)) + int(m.group(2)) / int(m.group(3))
    m = re.fullmatch(r"(\d+)/(\d+)", t)
    if m:
        return int(m.group(1)) / int(m.group(2))
    m = re.fullmatch(r"(\d+(?:\.\d+)?)", t)
    if m:
        return float(m.group(1))
    return None


def parse_depth_fields(depth_raw: str | None, usable_raw: str | None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "depth_min_mm": None,
        "depth_max_mm": None,
        "depth_notes": None,
        "usable_capacity_hint_mm": None,
    }
    if _unspecified(depth_raw) and _unspecified(usable_raw):
        return out

    notes_parts: list[str] = []
    values_mm: list[float] = []

    text = depth_raw or ""
    if not _unspecified(depth_raw):
        notes_parts.append(f"depth: {depth_raw}")

    # Collect explicit mm values.
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*mm", text, re.I):
        values_mm.append(float(m.group(1)))

    # Inch values including compound fractions before unit markers.
    for m in re.finditer(
        r"(\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)\s*(?:in\b|inch|inches|\")",
        text,
        re.I,
    ):
        inches = _parse_fractional_inches(m.group(1))
        if inches is not None:
            values_mm.append(_to_mm(inches, "in"))

    # Bare inch marks without word unit already handled; also 2" style mid-string.
    for m in re.finditer(r"(\d+(?:\.\d+)?)\"", text):
        values_mm.append(_to_mm(float(m.group(1)), "in"))

    if values_mm:
        out["depth_min_mm"] = min(values_mm)
        out["depth_max_mm"] = max(values_mm)
        if out["depth_min_mm"] == out["depth_max_mm"]:
            # Single measured depth: keep both equal for queryability.
            pass
    elif not _unspecified(depth_raw):
        # Non-numeric qualitative depth (e.g. "ample for QPS1").
        notes_parts.append("depth not numerically specified in research capture")

    usable_mm: list[float] = []
    if not _unspecified(usable_raw):
        notes_parts.append(f"usable: {usable_raw}")
        for m in re.finditer(r"(\d+(?:\.\d+)?)\s*mm", usable_raw or "", re.I):
            usable_mm.append(float(m.group(1)))
        for m in re.finditer(
            r"(\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)\s*(?:in\b|inch|inches|\")",
            usable_raw or "",
            re.I,
        ):
            inches = _parse_fractional_inches(m.group(1))
            if inches is not None:
                usable_mm.append(_to_mm(inches, "in"))
        if usable_mm:
            out["usable_capacity_hint_mm"] = min(usable_mm)
            # Prefer usable minimum as depth_min when more conservative.
            if out["depth_min_mm"] is None:
                out["depth_min_mm"] = min(usable_mm)
            else:
                out["depth_min_mm"] = min(out["depth_min_mm"], min(usable_mm))
            if out["depth_max_mm"] is None:
                out["depth_max_mm"] = max(usable_mm)

    if notes_parts:
        out["depth_notes"] = "; ".join(notes_parts)
    return out


def parse_outer_dims(outer_raw: str | None) -> dict[str, float | None]:
    out: dict[str, float | None] = {"width_mm": None, "height_mm": None, "depth_mm": None}
    if _unspecified(outer_raw):
        return out
    text = outer_raw or ""

    # Prefer first complete WxHxD triple in mm.
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*mm",
        text,
        re.I,
    )
    if m:
        out["width_mm"] = float(m.group(1))
        out["height_mm"] = float(m.group(2))
        out["depth_mm"] = float(m.group(3))
        return out

    m = re.search(
        r"(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*in",
        text,
        re.I,
    )
    if m:
        out["width_mm"] = _to_mm(float(m.group(1)), "in")
        out["height_mm"] = _to_mm(float(m.group(2)), "in")
        out["depth_mm"] = _to_mm(float(m.group(3)), "in")
        return out

    # Dual depth notation like 540×314×73/107mm
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*[×x]\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*mm",
        text,
        re.I,
    )
    if m:
        out["width_mm"] = float(m.group(1))
        out["height_mm"] = float(m.group(2))
        out["depth_mm"] = float(m.group(3))
        return out

    return out


def parse_weight_kg(build_raw: str | None) -> float | None:
    if _unspecified(build_raw):
        return None
    text = build_raw or ""
    m = re.search(r"(\d+(?:\.\d+)?)\s*kg", text, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*lb(?:\s+(\d+)\s*oz)?", text, re.I)
    if m:
        lb = float(m.group(1))
        oz = float(m.group(2) or 0)
        return round((lb + oz / 16.0) * 0.45359237, 3)
    return None


def parse_materials(build_raw: str | None) -> str | None:
    if _unspecified(build_raw):
        return None
    text = build_raw or ""
    # build pattern: weight; materials; finish/price...
    parts = [p.strip() for p in text.split(";")]
    if len(parts) >= 2 and not _unspecified(parts[1]):
        material = parts[1]
        # Reject pure price tokens.
        if re.search(r"^[$€£]", material):
            return None
        if re.fullmatch(r"\d{4}", material):
            return None
        return material[:500]
    return None


def map_format_family(raw_family: str, format_raw: str | None) -> str:
    key = (raw_family or "").strip().lower()
    if key in FORMAT_MAP:
        return FORMAT_MAP[key]
    fr = (format_raw or "").lower()
    if "buchla" in fr:
        return "buchla_200"
    if "serge" in fr:
        return "serge_4u"
    if "frac" in fr:
        return "frac"
    if "5u" in fr or re.search(r"\bmu\b", fr):
        return "mu_5u"
    return "eurorack"


def map_capacity_unit(raw_unit: str | None, format_family: str) -> str:
    if raw_unit and raw_unit in UNIT_MAP:
        return UNIT_MAP[raw_unit]
    defaults = {
        "eurorack": "hp",
        "intellijel_1u": "hp",
        "pulplogic_1u": "hp",
        "buchla_200": "buchla_panel",
        "serge_4u": "serge_panel",
        "mu_5u": "mu_space",
        "frac": "frac_width",
        "other": "custom",
    }
    return defaults[format_family]


def row_format_family(
    case_format: str,
    format_raw: str | None,
    row_index: int,
    rows_total: int,
    size_summary: str | None,
) -> str:
    """Detect Intellijel 1U trailing rows when research format is mixed."""
    fr = (format_raw or "").lower()
    summary = (size_summary or "").lower()
    if "intellijel 1u" in fr or ("1u" in summary and "intellijel" in fr):
        # Last row is the 1U row for Palette / Performance case layouts in this dataset.
        if rows_total >= 2 and row_index == rows_total - 1:
            return "intellijel_1u"
    return case_format


def mounting_flags(mounting: str | None, build_raw: str | None, power_raw: str | None) -> dict[str, Any]:
    text = " ".join(x for x in [mounting or "", build_raw or "", power_raw or ""] if x).lower()
    flags: dict[str, Any] = {
        "mounting_type": mounting.strip()[:80] if mounting and not _unspecified(mounting) else None,
        "portable": None,
        "removable_lid": None,
        "close_patched_lid": None,
        "integrated_stand": None,
        "rack_mountable": None,
    }
    if re.search(r"portable|travel|performance case|flight|road", text):
        flags["portable"] = True
    elif re.search(r"desktop|studio|skiff|boat|console", text) and "portable" not in text:
        flags["portable"] = False

    if re.search(r"removable lid|with lid|detachable lid", text):
        flags["removable_lid"] = True
    if re.search(r"close[- ]patched", text):
        flags["close_patched_lid"] = True
    if re.search(r"stand|folding stand|adjustable leg|legs", text):
        flags["integrated_stand"] = True
    if re.search(r"rack[- ]?mount|rack ears|rackear", text):
        flags["rack_mountable"] = True
    return flags


def parse_connector_count(power_raw: str | None) -> int | None:
    if _unspecified(power_raw):
        return None
    text = power_raw or ""
    patterns = [
        r"(\d+)\s+headers",
        r"(\d+)\s+shrouded headers",
        r"(\d+)\s+keyed connectors",
        r"(\d+)\s+connectors",
        r"(\d+)\s+sockets",
        r"(\d+)\s+power outlets",
        r"(\d+)\s+on busboard",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return int(m.group(1))
    m = re.search(r"(\d+)\s*\+\s*(\d+)\s+sockets", text, re.I)
    if m:
        return int(m.group(1)) + int(m.group(2))
    return None


def parse_power_watts(power_raw: str | None) -> float | None:
    if _unspecified(power_raw):
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*W\b", power_raw or "", re.I)
    if m:
        return float(m.group(1))
    return None


def parse_supply_type(power_raw: str | None, powered: bool | None) -> str | None:
    if powered is False:
        return "none"
    if _unspecified(power_raw):
        return None
    text = (power_raw or "").lower()
    if "none" in text[:20]:
        return "none"
    if "flying bus" in text:
        return "module_psu_flying_bus"
    if "external" in text or "brick" in text or "barrel" in text or "adapter" in text:
        return "external_brick"
    if "integrated" in text or "internal" in text or "built-in" in text:
        return "integrated"
    if powered:
        return "integrated"
    return None


def confidence_for_record(case: dict[str, Any], depth: dict[str, Any], power_present: bool) -> str:
    score = 0
    if case.get("total_hp"):
        score += 1
    if power_present:
        score += 1
    if depth.get("depth_max_mm") is not None:
        score += 1
    if (case.get("meta") or {}).get("pricing"):
        score += 1
    if score >= 3:
        return "medium"
    if score >= 1:
        return "low"
    return "low"


def policy_packet(
    *,
    content_hash: str,
    external_record_id: str,
    evidence_status: str = "UNKNOWN",
    license_status: str = "research_synthesis",
    notes: str | None = None,
) -> dict[str, Any]:
    packet = {
        "access_basis": "manual_research",
        "license_status": license_status,
        "evidence_status": evidence_status,
        "review_state": "pending",
        "observed_at": OBSERVED_AT,
        "retrieved_at": RETRIEVED_AT,
        "content_hash": content_hash,
        "normalizer_version": NORMALIZER_VERSION,
        "external_record_id": external_record_id,
    }
    if notes:
        packet["notes"] = notes
    return packet


def make_source(
    *,
    field_path: str,
    published_value: Any,
    normalized_value: Any,
    content_hash: str,
    external_record_id: str,
    confidence: str,
    evidence_status: str = "UNKNOWN",
    source_type: str = "research_synthesis",
    notes: str | None = None,
) -> dict[str, Any]:
    pub = None if published_value is None else str(published_value)
    norm = None if normalized_value is None else str(normalized_value)
    return {
        "source_type": source_type,
        "title": RESEARCH_SOURCE_TITLE,
        "url": RESEARCH_SOURCE_URL,
        "field_path": field_path,
        "published_value": pub,
        "normalized_value": norm,
        "confidence": confidence,
        "policy": policy_packet(
            content_hash=content_hash,
            external_record_id=external_record_id,
            evidence_status=evidence_status,
            notes=notes,
        ),
    }


def convert_case(case: dict[str, Any], doc_hash: str) -> dict[str, Any]:
    meta = case.get("meta") or {}
    manufacturer = case["brand"].strip()
    model = case["name"].strip()
    external_id = f"cases4patchhive:{manufacturer}:{model}".lower().replace(" ", "_")
    format_family = map_format_family(case.get("format_family") or "", meta.get("format_raw"))
    capacity_unit = map_capacity_unit(case.get("capacity_unit") or meta.get("capacity_unit"), format_family)
    capacity_value = float(case["total_hp"]) if case.get("total_hp") is not None else None

    depth = parse_depth_fields(meta.get("depth_raw"), meta.get("usable_depth_raw"))
    dims = parse_outer_dims(meta.get("outer_dims_raw"))
    weight_kg = parse_weight_kg(meta.get("build_raw"))
    materials = parse_materials(meta.get("build_raw"))
    flags = mounting_flags(meta.get("mounting"), meta.get("build_raw"), meta.get("power_raw"))

    hp_per_row = case.get("hp_per_row") or []
    rows_total = int(case.get("rows") or len(hp_per_row) or 1)
    rows: list[dict[str, Any]] = []
    for idx, cap in enumerate(hp_per_row):
        row_ff = row_format_family(
            format_family,
            meta.get("format_raw"),
            idx,
            rows_total,
            meta.get("size_summary"),
        )
        row_unit = "hp" if row_ff in {"eurorack", "intellijel_1u", "pulplogic_1u"} else capacity_unit
        rows.append(
            {
                "row_index": idx,
                "format_family": row_ff,
                "capacity_value": float(cap),
                "capacity_unit": row_unit,
                "usable_capacity_value": None,
                "depth_min_mm": depth["depth_min_mm"],
                "depth_max_mm": depth["depth_max_mm"],
                "notes": None,
            }
        )

    power_present = any(
        case.get(k) is not None for k in ("power_12v_ma", "power_neg12v_ma", "power_5v_ma")
    ) or bool(case.get("powered"))
    power_systems: list[dict[str, Any]] = []
    if case.get("powered") is False:
        power_systems.append(
            {
                "name": "primary",
                "supply_type": "none",
                "external_input": None,
                "busboard_type": None,
                "connector_count": None,
                "current_pos12_ma": None,
                "current_neg12_ma": None,
                "current_pos5_ma": None,
                "power_watts": None,
                "zoned_distribution": None,
                "protections": None,
                "notes": meta.get("power_raw"),
            }
        )
    elif case.get("powered") is True or power_present:
        zoned = None
        power_raw = meta.get("power_raw") or ""
        if re.search(r"zone", power_raw, re.I):
            zoned = True
        power_systems.append(
            {
                "name": "primary",
                "supply_type": parse_supply_type(power_raw, case.get("powered")),
                "external_input": None,
                "busboard_type": None,
                "connector_count": parse_connector_count(power_raw),
                "current_pos12_ma": case.get("power_12v_ma"),
                "current_neg12_ma": case.get("power_neg12v_ma"),
                "current_pos5_ma": case.get("power_5v_ma"),
                "power_watts": parse_power_watts(power_raw),
                "zoned_distribution": zoned,
                "protections": None,
                "notes": power_raw if not _unspecified(power_raw) else None,
            }
        )

    features: list[dict[str, Any]] = []
    if meta.get("release_year"):
        features.append(
            {
                "feature_key": "release_year",
                "feature_value": str(meta["release_year"]),
                "verified": False,
            }
        )
    if meta.get("format_raw"):
        features.append(
            {
                "feature_key": "format_raw",
                "feature_value": str(meta["format_raw"])[:500],
                "verified": False,
            }
        )
    if meta.get("kind"):
        features.append(
            {
                "feature_key": "kind",
                "feature_value": str(meta["kind"]),
                "verified": False,
            }
        )
    if meta.get("rail_voltage_nominal"):
        features.append(
            {
                "feature_key": "rail_voltage_nominal",
                "feature_value": str(meta["rail_voltage_nominal"]),
                "verified": False,
            }
        )

    conf = confidence_for_record(case, depth, power_present=any(
        case.get(k) is not None for k in ("power_12v_ma", "power_neg12v_ma", "power_5v_ma")
    ))

    revision_notes_parts = []
    if meta.get("size_raw") and not _unspecified(meta.get("size_raw")):
        revision_notes_parts.append(meta["size_raw"])
    if case.get("description"):
        revision_notes_parts.append(case["description"])

    revision = {
        "revision_key": "research-2026",
        "revision_label": "Cases4PatchHive research capture 2026",
        "row_count": rows_total,
        "capacity_value": capacity_value,
        "capacity_unit": capacity_unit,
        "usable_capacity_value": None,
        "depth_min_mm": depth["depth_min_mm"],
        "depth_max_mm": depth["depth_max_mm"],
        "depth_notes": depth["depth_notes"],
        "width_mm": dims["width_mm"],
        "height_mm": dims["height_mm"],
        "depth_mm": dims["depth_mm"],
        "weight_kg": weight_kg,
        "materials": materials,
        "mounting_type": flags["mounting_type"],
        "portable": flags["portable"],
        "removable_lid": flags["removable_lid"],
        "close_patched_lid": flags["close_patched_lid"],
        "integrated_stand": flags["integrated_stand"],
        "rack_mountable": flags["rack_mountable"],
        "notes": " · ".join(revision_notes_parts)[:4000] if revision_notes_parts else None,
        "confidence": conf,
    }

    # Field-level sources for identity + non-null technical values.
    sources: list[dict[str, Any]] = [
        make_source(
            field_path="manufacturer",
            published_value=manufacturer,
            normalized_value=manufacturer,
            content_hash=doc_hash,
            external_record_id=external_id,
            confidence=conf,
            notes="Research master-table manufacturer cell",
        ),
        make_source(
            field_path="model",
            published_value=model,
            normalized_value=model,
            content_hash=doc_hash,
            external_record_id=external_id,
            confidence=conf,
            notes="Research master-table model cell",
        ),
        make_source(
            field_path="format_family",
            published_value=meta.get("format_raw") or case.get("format_family"),
            normalized_value=format_family,
            content_hash=doc_hash,
            external_record_id=external_id,
            confidence=conf,
        ),
        make_source(
            field_path="revision.capacity_value",
            published_value=meta.get("size_summary") or capacity_value,
            normalized_value=capacity_value,
            content_hash=doc_hash,
            external_record_id=external_id,
            confidence=conf,
        ),
        make_source(
            field_path="revision.capacity_unit",
            published_value=case.get("capacity_unit") or meta.get("capacity_unit"),
            normalized_value=capacity_unit,
            content_hash=doc_hash,
            external_record_id=external_id,
            confidence=conf,
        ),
    ]

    if case.get("powered") is not None:
        sources.append(
            make_source(
                field_path="powered",
                published_value=meta.get("power_raw"),
                normalized_value=case.get("powered"),
                content_hash=doc_hash,
                external_record_id=external_id,
                confidence=conf,
            )
        )
    if depth["depth_min_mm"] is not None:
        sources.append(
            make_source(
                field_path="revision.depth_min_mm",
                published_value=meta.get("depth_raw") or meta.get("usable_depth_raw"),
                normalized_value=depth["depth_min_mm"],
                content_hash=doc_hash,
                external_record_id=external_id,
                confidence=conf,
            )
        )
    if depth["depth_max_mm"] is not None:
        sources.append(
            make_source(
                field_path="revision.depth_max_mm",
                published_value=meta.get("depth_raw"),
                normalized_value=depth["depth_max_mm"],
                content_hash=doc_hash,
                external_record_id=external_id,
                confidence=conf,
            )
        )
    for field, value in (
        ("revision.width_mm", dims["width_mm"]),
        ("revision.height_mm", dims["height_mm"]),
        ("revision.depth_mm", dims["depth_mm"]),
        ("revision.weight_kg", weight_kg),
        ("revision.materials", materials),
    ):
        if value is not None:
            sources.append(
                make_source(
                    field_path=field,
                    published_value=meta.get("outer_dims_raw") if "mm" in field else meta.get("build_raw"),
                    normalized_value=value,
                    content_hash=doc_hash,
                    external_record_id=external_id,
                    confidence=conf,
                )
            )

    if power_systems:
        ps = power_systems[0]
        for field, value in (
            ("power_systems[0].current_pos12_ma", ps.get("current_pos12_ma")),
            ("power_systems[0].current_neg12_ma", ps.get("current_neg12_ma")),
            ("power_systems[0].current_pos5_ma", ps.get("current_pos5_ma")),
            ("power_systems[0].connector_count", ps.get("connector_count")),
            ("power_systems[0].power_watts", ps.get("power_watts")),
            ("power_systems[0].supply_type", ps.get("supply_type")),
        ):
            if value is not None:
                sources.append(
                    make_source(
                        field_path=field,
                        published_value=meta.get("power_raw"),
                        normalized_value=value,
                        content_hash=doc_hash,
                        external_record_id=external_id,
                        confidence=conf,
                    )
                )

    prices: list[dict[str, Any]] = []
    pricing = meta.get("pricing") or {}
    for key, amount in pricing.items():
        if amount is None:
            continue
        if key.endswith("_usd"):
            currency = "USD"
        elif key.endswith("_eur"):
            currency = "EUR"
        elif key.endswith("_gbp"):
            currency = "GBP"
        else:
            currency = "USD"
        price_type = "msrp" if key.startswith("official") else "street"
        prices.append(
            {
                "source_name": "Cases4PatchHive research synthesis",
                "source_url": RESEARCH_SOURCE_URL,
                "amount": f"{float(amount):.2f}",
                "currency": currency,
                "region": None,
                "price_type": price_type,
                "in_stock": None,
                "captured_at": OBSERVED_AT,
            }
        )
        sources.append(
            make_source(
                field_path=f"prices.{price_type}.{currency}",
                published_value=meta.get("build_raw"),
                normalized_value=f"{amount} {currency}",
                content_hash=doc_hash,
                external_record_id=external_id,
                confidence=conf,
                evidence_status="UNKNOWN",
            )
        )

    record = {
        "manufacturer": manufacturer,
        "model": model,
        "format_family": format_family,
        "production_status": "unknown",
        "powered": case.get("powered"),
        "official_url": case.get("manufacturer_url"),
        "image_url": None,
        "revision": revision,
        "rows": rows,
        "power_systems": power_systems,
        "features": features,
        "sources": sources,
        "prices": prices,
    }
    return record


def build_source_manifest(
    *,
    research_md: Path,
    research_json: Path,
    seed_path: Path,
    doc_hash: str,
    research_json_hash: str,
    seed_hash: str,
    case_count: int,
    source_packet_count: int,
) -> dict[str, Any]:
    return {
        "manifest_version": "1.0",
        "dataset_version": DATASET_VERSION,
        "normalizer_version": NORMALIZER_VERSION,
        "generated_at": GENERATED_AT,
        "purpose": (
            "Source and licensing manifest for the first modular case catalog seed. "
            "Research synthesis supports candidate catalog population; it is not "
            "manufacturer-verified canonical truth."
        ),
        "inputs": [
            {
                "path": str(research_md.relative_to(REPO_ROOT)),
                "role": "primary_research_report",
                "sha256": doc_hash,
                "access_basis": "manual_research",
                "license_status": "research_synthesis",
                "redistribution": (
                    "Internal research notes compiled from public manufacturer and "
                    "retailer observations. Do not republish as official manufacturer copy."
                ),
            },
            {
                "path": str(research_json.relative_to(REPO_ROOT)),
                "role": "parsed_research_fixture",
                "sha256": research_json_hash,
                "access_basis": "manual_research",
                "license_status": "research_synthesis",
            },
            {
                "path": str(seed_path.relative_to(REPO_ROOT)),
                "role": "canonical_import_seed",
                "sha256": seed_hash,
                "access_basis": "manual_research",
                "license_status": "research_synthesis",
            },
        ],
        "sources": [
            {
                "source_id": "cases4patchhive-2026",
                "source_type": "research_synthesis",
                "source_name": RESEARCH_SOURCE_TITLE,
                "source_url": RESEARCH_SOURCE_URL,
                "access_basis": "manual_research",
                "license_status": "research_synthesis",
                "evidence_status": "UNKNOWN",
                "review_state": "pending",
                "content_hash": doc_hash,
                "fields_permitted": [
                    "manufacturer",
                    "model",
                    "format_family",
                    "capacity",
                    "row layout",
                    "depth",
                    "outer dimensions",
                    "weight",
                    "materials",
                    "power rails when explicitly published in research capture",
                    "price observations",
                    "mounting notes",
                ],
                "fields_restricted": [
                    "panel images",
                    "verbatim retailer marketing copy",
                    "manufacturer trademarks as branding assets",
                ],
                "notes": (
                    "Compiled for PatchHive catalog bootstrap. Field-level packets on each "
                    "seed record inherit this document hash. Official manufacturer pages and "
                    "manuals remain higher authority for verified publication."
                ),
            }
        ],
        "policy": {
            "unknown_values": "null_only",
            "verified_publication_requires": [
                "official_publication or higher access_basis",
                "non-unknown license_status",
                "content_hash",
                "review_state accepted",
            ],
            "seed_publication_state": "research_candidate_not_verified_canonical",
        },
        "counts": {
            "cases": case_count,
            "field_source_packets": source_packet_count,
        },
    }


def coverage_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(records)
    def pct(count: int) -> float:
        return round(100.0 * count / n, 1) if n else 0.0

    powered_true = sum(1 for r in records if r.get("powered") is True)
    powered_false = sum(1 for r in records if r.get("powered") is False)
    powered_null = sum(1 for r in records if r.get("powered") is None)
    with_pos12 = sum(
        1
        for r in records
        if any(
            (ps.get("current_pos12_ma") is not None)
            for ps in (r.get("power_systems") or [])
        )
    )
    with_depth = sum(
        1
        for r in records
        if (r.get("revision") or {}).get("depth_max_mm") is not None
        or (r.get("revision") or {}).get("depth_min_mm") is not None
    )
    with_dims = sum(
        1
        for r in records
        if (r.get("revision") or {}).get("width_mm") is not None
    )
    with_weight = sum(1 for r in records if (r.get("revision") or {}).get("weight_kg") is not None)
    with_price = sum(1 for r in records if r.get("prices"))
    with_sources = sum(1 for r in records if r.get("sources"))
    source_packets = sum(len(r.get("sources") or []) for r in records)

    by_format: dict[str, int] = {}
    for r in records:
        by_format[r["format_family"]] = by_format.get(r["format_family"], 0) + 1

    by_confidence: dict[str, int] = {}
    for r in records:
        conf = (r.get("revision") or {}).get("confidence", "unknown")
        by_confidence[conf] = by_confidence.get(conf, 0) + 1

    return {
        "dataset_version": DATASET_VERSION,
        "case_count": n,
        "format_family_counts": dict(sorted(by_format.items())),
        "confidence_counts": dict(sorted(by_confidence.items())),
        "field_coverage": {
            "powered_true": {"count": powered_true, "pct": pct(powered_true)},
            "powered_false": {"count": powered_false, "pct": pct(powered_false)},
            "powered_null": {"count": powered_null, "pct": pct(powered_null)},
            "power_pos12_ma": {"count": with_pos12, "pct": pct(with_pos12)},
            "depth_mm": {"count": with_depth, "pct": pct(with_depth)},
            "outer_width_mm": {"count": with_dims, "pct": pct(with_dims)},
            "weight_kg": {"count": with_weight, "pct": pct(with_weight)},
            "price_observation": {"count": with_price, "pct": pct(with_price)},
            "source_packets_present": {"count": with_sources, "pct": pct(with_sources)},
        },
        "source_packet_total": source_packets,
        "mean_source_packets_per_case": round(source_packets / n, 2) if n else 0,
        "publication_state": "research_candidate_not_verified_canonical",
        "notes": [
            "Coverage measures normalized seed fields, not manufacturer-verified completeness.",
            "Null remains the honest state for unspecified research cells.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-json", type=Path, default=DEFAULT_RESEARCH)
    parser.add_argument("--research-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--seed-out", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--sources-out", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--coverage-out", type=Path, default=DEFAULT_COVERAGE)
    args = parser.parse_args(argv)

    if not args.research_json.is_file():
        print(f"error: research JSON not found: {args.research_json}", file=sys.stderr)
        return 1
    if not args.research_md.is_file():
        print(f"error: research markdown not found: {args.research_md}", file=sys.stderr)
        return 1

    research = json.loads(args.research_json.read_text(encoding="utf-8"))
    cases = research["cases"] if isinstance(research, dict) else research
    doc_hash = sha256_file(args.research_md)
    research_json_hash = sha256_file(args.research_json)

    records = [convert_case(case, doc_hash) for case in cases]
    payload = {
        "dataset_version": DATASET_VERSION,
        "status": "research_candidate_not_verified_canonical",
        "normalizer_version": NORMALIZER_VERSION,
        "source_document": str(args.research_md.relative_to(REPO_ROOT)),
        "source_document_sha256": doc_hash,
        "research_fixture": str(args.research_json.relative_to(REPO_ROOT)),
        "research_fixture_sha256": research_json_hash,
        "case_count": len(records),
        "generated_at": GENERATED_AT,
        "cases": records,
    }

    args.seed_out.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    args.seed_out.write_text(rendered, encoding="utf-8")
    seed_hash = sha256_file(args.seed_out)

    source_packets = sum(len(r.get("sources") or []) for r in records)
    manifest = build_source_manifest(
        research_md=args.research_md,
        research_json=args.research_json,
        seed_path=args.seed_out,
        doc_hash=doc_hash,
        research_json_hash=research_json_hash,
        seed_hash=seed_hash,
        case_count=len(records),
        source_packet_count=source_packets,
    )
    args.sources_out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    coverage = coverage_stats(records)
    coverage["seed_sha256"] = seed_hash
    coverage["source_document_sha256"] = doc_hash
    args.coverage_out.write_text(json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "cases": len(records),
                "seed": str(args.seed_out),
                "seed_sha256": seed_hash,
                "sources": str(args.sources_out),
                "coverage": str(args.coverage_out),
                "source_packets": source_packets,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
