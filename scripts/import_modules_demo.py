#!/usr/bin/env python3
"""Import fixtures/modules_demo_seed.json into the modules table (idempotent by brand+name+source)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT = REPO / "fixtures" / "modules_demo_seed.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not args.input.is_file():
        print(f"error: not found: {args.input}", file=sys.stderr)
        return 1

    sys.path.insert(0, str(REPO / "backend"))
    from sqlalchemy import create_engine, text
    from core.config import settings

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    records = payload.get("modules") or []
    engine = create_engine(settings.database_url)
    inserted = 0
    updated = 0

    with engine.begin() as conn:
        if args.dry_run:
            # count only
            for rec in records:
                brand = rec["brand"].strip()
                name = rec["name"].strip()
                source = rec.get("source", "DemoSeed")
                exists = conn.execute(
                    text(
                        "SELECT id FROM modules WHERE brand=:b AND name=:n AND source=:s LIMIT 1"
                    ),
                    {"b": brand, "n": name, "s": source},
                ).first()
                if exists:
                    updated += 1
                else:
                    inserted += 1
            conn.rollback()
        else:
            for rec in records:
                brand = rec["brand"].strip()
                name = rec["name"].strip()
                source = rec.get("source", "DemoSeed")
                exists = conn.execute(
                    text(
                        "SELECT id FROM modules WHERE brand=:b AND name=:n AND source=:s LIMIT 1"
                    ),
                    {"b": brand, "n": name, "s": source},
                ).first()
                params = {
                    "brand": brand,
                    "name": name,
                    "hp": rec["hp"],
                    "module_type": rec["module_type"],
                    "power_12v_ma": rec.get("power_12v_ma"),
                    "power_neg12v_ma": rec.get("power_neg12v_ma"),
                    "power_5v_ma": rec.get("power_5v_ma"),
                    "depth_mm": rec.get("depth_mm"),
                    "io_ports": json.dumps(rec.get("io_ports") or []),
                    "tags": json.dumps(rec.get("tags") or []),
                    "description": rec.get("description"),
                    "source": source,
                    "source_reference": rec.get("source_reference") or str(args.input),
                }
                if exists:
                    conn.execute(
                        text(
                            """
                            UPDATE modules SET
                              hp=:hp, module_type=:module_type,
                              power_12v_ma=:power_12v_ma, power_neg12v_ma=:power_neg12v_ma,
                              power_5v_ma=:power_5v_ma, depth_mm=:depth_mm,
                              io_ports=CAST(:io_ports AS json), tags=CAST(:tags AS json),
                              description=:description, source_reference=:source_reference,
                              updated_at=NOW()
                            WHERE id=:id
                            """
                        ),
                        {**params, "id": exists[0]},
                    )
                    updated += 1
                else:
                    conn.execute(
                        text(
                            """
                            INSERT INTO modules (
                              brand, name, hp, module_type,
                              power_12v_ma, power_neg12v_ma, power_5v_ma, depth_mm,
                              io_ports, tags, description, source, source_reference,
                              status, imported_at, created_at, updated_at
                            ) VALUES (
                              :brand, :name, :hp, :module_type,
                              :power_12v_ma, :power_neg12v_ma, :power_5v_ma, :depth_mm,
                              CAST(:io_ports AS json), CAST(:tags AS json), :description,
                              :source, :source_reference,
                              'active', NOW(), NOW(), NOW()
                            )
                            """
                        ),
                        params,
                    )
                    inserted += 1

    print(
        json.dumps(
            {
                "status": "success",
                "dry_run": bool(args.dry_run),
                "input": str(args.input),
                "input_records": len(records),
                "inserted": inserted,
                "updated": updated,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
