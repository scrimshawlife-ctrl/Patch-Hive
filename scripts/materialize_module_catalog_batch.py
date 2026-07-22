#!/usr/bin/env python3
"""Batch-materialize HP-known module_catalog rows into full modules.

Fail-closed: never invents HP/power/depth. Idempotent by brand+name.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brand", default=None)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument(
        "--include-unknown-hp",
        action="store_true",
        help="Also attempt null-HP rows (they will fail 422; default skip)",
    )
    parser.add_argument("--receipt", type=Path, default=None)
    args = parser.parse_args(argv)

    sys.path.insert(0, str(REPO / "backend"))
    from core.database import SessionLocal
    from modules.catalog_routes import materialize_catalog_batch

    db = SessionLocal()
    try:
        receipt = materialize_catalog_batch(
            db,
            brand=args.brand,
            hp_known_only=not args.include_unknown_hp,
            limit=args.limit,
        )
    finally:
        db.close()

    print(json.dumps(receipt, indent=2))
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0 if receipt.get("status") in ("success", "partial") else 1


if __name__ == "__main__":
    raise SystemExit(main())
