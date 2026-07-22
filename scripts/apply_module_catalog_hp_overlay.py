#!/usr/bin/env python3
"""Apply module_catalog HP overlay (fill-null only)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overlay",
        type=Path,
        default=REPO / "data/synth-catalog/overlays/module-catalog-hp-v1.json",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--receipt", type=Path, default=None)
    args = parser.parse_args(argv)

    data = json.loads(args.overlay.read_text(encoding="utf-8"))
    entries = data.get("entries") or []

    sys.path.insert(0, str(REPO / "backend"))
    from sqlalchemy import create_engine, text
    from core.config import settings

    engine = create_engine(settings.database_url)
    updated = 0
    skipped = 0
    missing = 0
    samples = []

    with engine.begin() as conn:
        for e in entries:
            if e.get("hp") is None:
                skipped += 1
                continue
            slug = (e.get("slug") or "").strip()
            brand = (e.get("brand") or "").strip()
            name = (e.get("name") or "").strip()
            hp = int(e["hp"])
            row = None
            if slug:
                row = conn.execute(
                    text("SELECT id, hp FROM module_catalog WHERE slug=:s LIMIT 1"),
                    {"s": slug},
                ).mappings().first()
            if not row and brand and name:
                row = conn.execute(
                    text(
                        "SELECT id, hp FROM module_catalog WHERE brand=:b AND name=:n LIMIT 1"
                    ),
                    {"b": brand, "n": name},
                ).mappings().first()
            if not row:
                missing += 1
                continue
            if row["hp"] is not None:
                skipped += 1
                continue
            if not args.dry_run:
                conn.execute(
                    text(
                        "UPDATE module_catalog SET hp=:hp, updated_at=NOW() WHERE id=:id"
                    ),
                    {"hp": hp, "id": row["id"]},
                )
            updated += 1
            if len(samples) < 20:
                samples.append({"slug": slug or row["id"], "hp": hp})
        if args.dry_run:
            conn.rollback()

    receipt = {
        "status": "success",
        "dry_run": args.dry_run,
        "overlay": str(args.overlay),
        "entries": len(entries),
        "updated_hp": updated,
        "skipped": skipped,
        "missing": missing,
        "samples": samples,
    }
    print(json.dumps(receipt, indent=2))
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
