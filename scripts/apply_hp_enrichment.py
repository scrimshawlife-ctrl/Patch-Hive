#!/usr/bin/env python3
"""Apply Hermes/Firecrawl HP enrichment results to module_catalog (fail-closed).

Uses raw SQL to avoid full ORM graph bootstrap.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--allow-inferred",
        action="store_true",
        help="Also apply provenance=INFERRED (default OBSERVED only)",
    )
    parser.add_argument("--receipt", type=Path, default=None)
    args = parser.parse_args(argv)

    data = json.loads(args.results.read_text(encoding="utf-8"))
    rows = data.get("results") or []

    sys.path.insert(0, str(REPO / "backend"))
    from sqlalchemy import create_engine, text
    from core.config import settings

    engine = create_engine(settings.database_url)
    updated = 0
    skipped = 0
    missing = 0
    samples = []

    with engine.begin() as conn:
        for r in rows:
            if r.get("status") != "found" or r.get("hp") is None:
                skipped += 1
                continue
            if not args.allow_inferred and r.get("provenance") != "OBSERVED":
                skipped += 1
                continue
            slug = (r.get("slug") or "").strip()
            brand = (r.get("brand") or "").strip()
            name = (r.get("name") or "").strip()
            hp = int(r["hp"])

            row = None
            if slug:
                row = conn.execute(
                    text(
                        "SELECT id, slug, brand, name, hp FROM module_catalog WHERE slug=:s LIMIT 1"
                    ),
                    {"s": slug},
                ).mappings().first()
            if not row and brand and name:
                row = conn.execute(
                    text(
                        "SELECT id, slug, brand, name, hp FROM module_catalog "
                        "WHERE brand=:b AND name=:n LIMIT 1"
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
            if len(samples) < 25:
                samples.append(
                    {
                        "slug": row["slug"],
                        "hp": hp,
                        "source_url": r.get("source_url"),
                        "provenance": r.get("provenance"),
                    }
                )
        if args.dry_run:
            conn.rollback()

    receipt = {
        "status": "success",
        "dry_run": args.dry_run,
        "results_path": str(args.results),
        "input_results": len(rows),
        "updated_hp": updated,
        "skipped": skipped,
        "missing_catalog": missing,
        "samples": samples,
    }
    print(json.dumps(receipt, indent=2))
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
