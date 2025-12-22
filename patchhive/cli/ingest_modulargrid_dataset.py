from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from patchhive.gallery.store_v2 import ModuleGalleryStoreV2, _meta
from patchhive.gallery.schemas_gallery_v2 import (
    ModuleGalleryRevision,
    ModuleIdentity,
    ModuleAttachment,
    ModuleAttachmentType,
    FieldStatus,
    ProvenanceType,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = _slug_re.sub("-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "unnamed"


def stable_module_key(manufacturer: str, module_name: str, hp: int) -> str:
    """Deterministic module key for gallery."""
    mfr_slug = slugify(manufacturer)
    mod_slug = slugify(module_name)
    return f"{mfr_slug}__{mod_slug}__{hp}hp"


def norm_list_csv(s: str) -> List[str]:
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


def normalize_secondary_functions(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return norm_list_csv(str(value))


def normalize_optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pick_first_key(payload: Dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in payload:
            return payload.get(key)
    return None


def stable_module_id(manufacturer: str, module_name: str) -> str:
    return sha256_hex(f"{manufacturer}::{module_name}")


# ----------------------------
# Sketch generator (plain panel w/ optional jack list)
# ----------------------------

SVG_HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>"""


def gen_panel_svg(
    title: str,
    manufacturer: str,
    hp: int,
    jacks: List[Tuple[str, str]],  # (label, type) type: "in"|"out"|"cv"|"gate" etc.
    width_per_hp_px: int = 14,     # simple scale
    height_px: int = 380,
) -> str:
    width_px = max(60, hp * width_per_hp_px)
    pad = 14
    text_y = 22

    # Simple grid: if jacks exist, place them in rows. If none, leave empty "JACKS TBD".
    jack_r = 10
    cols = 2 if width_px < 140 else 3 if width_px < 210 else 4
    col_w = (width_px - 2 * pad) / cols
    row_h = 34

    def esc(s: str) -> str:
        return (
            s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
        )

    svg = [SVG_HEADER]
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" viewBox="0 0 {width_px} {height_px}">'
    )
    # panel body
    svg.append(f'<rect x="1" y="1" width="{width_px-2}" height="{height_px-2}" rx="8" ry="8" fill="#f7f7f7" stroke="#111" stroke-width="2"/>')
    # header text
    svg.append(f'<text x="{pad}" y="{text_y}" font-family="Arial, sans-serif" font-size="14" fill="#111">{esc(manufacturer)}</text>')
    svg.append(f'<text x="{pad}" y="{text_y+18}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#111">{esc(title)}</text>')
    svg.append(f'<text x="{pad}" y="{text_y+36}" font-family="Arial, sans-serif" font-size="12" fill="#333">{hp} HP</text>')

    # jack area
    base_y = text_y + 60
    if not jacks:
        svg.append(f'<text x="{pad}" y="{base_y+18}" font-family="Arial, sans-serif" font-size="12" fill="#666">JACKS: TBD</text>')
    else:
        for i, (label, jtype) in enumerate(jacks):
            r = i // cols
            c = i % cols
            cx = pad + c * col_w + 12
            cy = base_y + r * row_h + 16

            stroke = "#111"  # Keep it plain for now

            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{jack_r}" fill="#fff" stroke="{stroke}" stroke-width="2"/>')
            svg.append(f'<text x="{cx+18}" y="{cy+4}" font-family="Arial, sans-serif" font-size="11" fill="#111">{esc(label)}</text>')

    svg.append("</svg>")
    return "\n".join(svg)


def ingest_modulargrid_dataset(
    src_json: Path,
    gallery_root: str,
    *,
    source_name: str = "ModularGrid Top 100",
    database_version: str = "unknown",
    library_root: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ingest ModularGrid dataset into PatchHive gallery v2.

    Creates:
    - Gallery revisions for each module
    - Plain sketch SVG attachments (jacks TBD until discovered)
    - Tags based on primary/secondary functions
    """
    with src_json.open("r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    modules = data.get("modules", [])
    database_version = str(meta.get("database_version", database_version))
    source_name = str(meta.get("source", source_name))

    store = ModuleGalleryStoreV2(gallery_root)
    library_root_path = Path(library_root) if library_root else Path(gallery_root) / "module_library"
    gallery_entries_path = Path(gallery_root) / "gallery_entries"
    library_root_path.mkdir(parents=True, exist_ok=True)
    gallery_entries_path.mkdir(parents=True, exist_ok=True)

    ingested = 0
    skipped = 0

    for m in modules:
        manufacturer = str(m.get("manufacturer", "")).strip()
        module_name = str(m.get("module_name", "")).strip()
        if not manufacturer or not module_name:
            skipped += 1
            continue

        hp_raw = m.get("hp_width")
        hp = int(hp_raw) if hp_raw not in (None, "") else None
        if not hp:
            skipped += 1
            continue
        depth_raw = m.get("depth_mm")
        depth_mm = int(depth_raw) if depth_raw not in (None, "") else None
        power_plus12 = normalize_optional_float(
            pick_first_key(m, ["power_+12v_ma", "+12v_ma", "power_plus12v_ma", "power_12v_ma"])
        )
        power_minus12 = normalize_optional_float(
            pick_first_key(m, ["power_-12v_ma", "-12v_ma", "power_minus12v_ma", "power_12v_neg_ma"])
        )
        power_plus5 = normalize_optional_float(
            pick_first_key(m, ["power_+5v_ma", "+5v_ma", "power_plus5v_ma", "power_5v_ma"])
        )

        module_key = stable_module_key(manufacturer, module_name, hp)

        # Check if already exists
        existing = store.read_latest(module_key)
        if existing:
            print(f"Skipping existing: {module_key}")
            skipped += 1
            continue

        primary = str(m.get("primary_function", "")).strip() or "Unknown"
        secondary = normalize_secondary_functions(m.get("secondary_functions"))
        price_usd = normalize_optional_float(m.get("price_usd"))
        description = str(m.get("description", "")).strip() or None

        # Tags: lightweight capability map for search + patch-gen filters
        tags = sorted(set(
            ([primary] if primary else [])
            + secondary
            + [manufacturer]
        ), key=lambda x: x.lower())

        evidence_ref = f"{source_name}::{database_version}::{module_key}"

        # Create identity
        identity = ModuleIdentity(
            manufacturer=manufacturer,
            name=module_name,
            hp=hp,
            module_key=module_key,
        )

        # Generate plain sketch (no jacks yet)
        sketch_filename = f"{module_key}_sketch.svg"
        svg = gen_panel_svg(
            title=module_name,
            manufacturer=manufacturer,
            hp=hp,
            jacks=[],  # TBD - will be populated when jacks discovered
        )

        # Write sketch to gallery assets
        svg_path = store.write_asset(module_key, sketch_filename, svg.encode("utf-8"))

        # Create sketch attachment
        sketch_att = ModuleAttachment(
            attachment_id="att.sketch.generated",
            type=ModuleAttachmentType.sketch_svg,
            ref=svg_path,
            source="derived",
            meta=_meta(
                "ingest_modulargrid_dataset.v1",
                evidence_ref,
                ProvenanceType.scraped,
                status=FieldStatus.inferred,
            ),
        )

        # Create revision (no jacks yet - will be added later)
        rev = ModuleGalleryRevision(
            module_key=module_key,
            revision_id="",  # will be set by append_revision
            version=0,
            identity=identity,
            tags=tags,
            jacks=[],  # Empty until discovered via photo parse/manual edit
            attachments=[sketch_att],
            meta=_meta(
                "ingest_modulargrid_dataset.v1",
                evidence_ref,
                ProvenanceType.scraped,
                status=FieldStatus.inferred,
            ),
        )

        # Append to store
        stored = store.append_revision(rev, evidence_ref=evidence_ref)
        print(f"Ingested: {module_key} (v{stored.version}, rev {stored.revision_id})")
        ingested += 1

        module_id = stable_module_id(manufacturer, module_name)
        imported_at = utc_now_iso()

        library_entry = {
            "module_id": module_id,
            "manufacturer": manufacturer,
            "module_name": module_name,
            "physical": {
                "hp": hp,
                "depth_mm": depth_mm,
            },
            "power": {
                "+12v_ma": power_plus12,
                "-12v_ma": power_minus12,
                "+5v_ma": power_plus5,
            },
            "primary_function": primary or None,
            "secondary_functions": secondary,
            "price_usd": price_usd,
            "description": description,
            "tags": tags,
            "jacks": [],
            "provenance": {
                "source": source_name,
                "database_version": database_version,
                "imported_at": imported_at,
            },
        }

        gallery_entry = {
            "module_id": module_id,
            "display_name": module_name,
            "manufacturer": manufacturer,
            "hp": hp,
            "primary_function": primary or None,
            "secondary_functions": secondary,
            "panel_image": None,
            "panel_sketch": svg,
            "user_uploaded_images": [],
            "tags": tags,
            "provenance": {
                "source": source_name,
                "database_version": database_version,
                "imported_at": imported_at,
            },
        }

        (library_root_path / f"{module_id}.json").write_text(
            json.dumps(library_entry, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (gallery_entries_path / f"{module_id}.json").write_text(
            json.dumps(gallery_entry, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    manifest = {
        "kind": "patchhive.ingest_manifest",
        "imported_at": utc_now_iso(),
        "source": source_name,
        "database_version": database_version,
        "modules_ingested": ingested,
        "modules_skipped": skipped,
        "gallery_root": gallery_root,
        "module_library_root": str(library_root_path),
        "gallery_entries_root": str(gallery_entries_path),
    }

    # Write manifest
    manifest_path = Path(gallery_root) / "ingest_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Ingest ModularGrid Top 100 dataset into PatchHive gallery"
    )
    ap.add_argument("--src-json", required=True, help="Path to eurorack_modules_database.json")
    ap.add_argument("--gallery-root", required=True, help="Gallery root directory")
    ap.add_argument(
        "--library-root",
        help="Module library output directory (defaults to {gallery_root}/module_library)",
    )
    args = ap.parse_args()

    manifest = ingest_modulargrid_dataset(
        Path(args.src_json),
        args.gallery_root,
        library_root=args.library_root,
    )

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
