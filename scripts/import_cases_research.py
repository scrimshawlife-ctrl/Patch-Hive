#!/usr/bin/env python3
"""
Import fixtures/cases_research_2026.json into the cases table.

Upserts by (brand, name). Default source filter for replace: ResearchCSV.

Usage (from repo root, with backend venv + DATABASE_URL):

  cd backend && python -m pip install -e '.[dev]'   # once
  cd .. && python scripts/import_cases_research.py
  python scripts/import_cases_research.py --dry-run
  python scripts/import_cases_research.py --replace-source
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = REPO_ROOT / "fixtures" / "cases_research_2026.json"
BACKEND = REPO_ROOT / "backend"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate fixture against CaseCreate schema only",
    )
    parser.add_argument(
        "--replace-source",
        action="store_true",
        help="Delete existing rows with source=ResearchCSV before import",
    )
    args = parser.parse_args(argv)

    if not args.fixture.is_file():
        print(f"error: fixture not found: {args.fixture}", file=sys.stderr)
        return 1

    payload = json.loads(args.fixture.read_text(encoding="utf-8"))
    cases = payload.get("cases") or []
    if not cases:
        print("error: fixture has no cases", file=sys.stderr)
        return 1

    sys.path.insert(0, str(BACKEND))
    from cases.schemas import CaseCreate  # noqa: E402

    validated: list[CaseCreate] = []
    for raw in cases:
        validated.append(CaseCreate.model_validate(raw))
    print(f"validated {len(validated)} CaseCreate records")

    if args.dry_run:
        eurorack = sum(1 for c in cases if (c.get("meta") or {}).get("format_family") == "Eurorack")
        print(f"dry-run OK · eurorack={eurorack} · other={len(cases) - eurorack}")
        return 0

    # Prefer raw SQL upsert so we do not need the full relationship mapper graph.
    from datetime import datetime, timezone

    import os

    from sqlalchemy import create_engine, text
    from core.config import settings  # noqa: E402

    db_url = os.environ.get("DATABASE_URL") or settings.database_url
    engine = create_engine(db_url)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    try:
        with engine.begin() as conn:
            if args.replace_source:
                deleted = conn.execute(
                    text("DELETE FROM cases WHERE source = :src"),
                    {"src": "ResearchCSV"},
                ).rowcount
                print(f"deleted {deleted} existing ResearchCSV cases")

            existing_rows = conn.execute(
                text("SELECT id, brand, name FROM cases")
            ).fetchall()
            existing = {(r.brand, r.name): r.id for r in existing_rows}

            inserted = updated = 0
            for item in validated:
                data = item.model_dump()
                meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
                if not data.get("format_family"):
                    data["format_family"] = meta.get("format_family") or "Eurorack"
                if not data.get("capacity_unit"):
                    data["capacity_unit"] = meta.get("capacity_unit") or "hp"
                if data.get("powered") is None:
                    if "powered" in meta:
                        data["powered"] = bool(meta.get("powered"))
                    else:
                        name_l = (data.get("name") or "").lower()
                        data["powered"] = "no power" not in name_l and "unpowered" not in name_l
                key = (data["brand"], data["name"])
                params = {
                    **data,
                    "meta": json.dumps(data["meta"]) if data.get("meta") is not None else None,
                    "hp_per_row": json.dumps(data["hp_per_row"]),
                    "now": now,
                }
                if key not in existing:
                    conn.execute(
                        text(
                            """
                            INSERT INTO cases (
                              brand, name, total_hp, "rows", hp_per_row,
                              format_family, capacity_unit, powered,
                              power_12v_ma, power_neg12v_ma, power_5v_ma,
                              description, manufacturer_url, meta,
                              source, source_reference, created_at, updated_at
                            ) VALUES (
                              :brand, :name, :total_hp, :rows, CAST(:hp_per_row AS json),
                              :format_family, :capacity_unit, :powered,
                              :power_12v_ma, :power_neg12v_ma, :power_5v_ma,
                              :description, :manufacturer_url, CAST(:meta AS json),
                              :source, :source_reference, :now, :now
                            )
                            """
                        ),
                        params,
                    )
                    inserted += 1
                else:
                    params["id"] = existing[key]
                    conn.execute(
                        text(
                            """
                            UPDATE cases SET
                              total_hp = :total_hp,
                              "rows" = :rows,
                              hp_per_row = CAST(:hp_per_row AS json),
                              format_family = :format_family,
                              capacity_unit = :capacity_unit,
                              powered = :powered,
                              power_12v_ma = :power_12v_ma,
                              power_neg12v_ma = :power_neg12v_ma,
                              power_5v_ma = :power_5v_ma,
                              description = :description,
                              manufacturer_url = :manufacturer_url,
                              meta = CAST(:meta AS json),
                              source = :source,
                              source_reference = :source_reference,
                              updated_at = :now
                            WHERE id = :id
                            """
                        ),
                        params,
                    )
                    updated += 1
        print(f"import complete · inserted={inserted} · updated={updated} · total={len(validated)}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
