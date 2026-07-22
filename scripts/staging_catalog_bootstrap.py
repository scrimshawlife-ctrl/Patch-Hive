#!/usr/bin/env python3
"""Staging catalog rebuild chain (fail-closed, idempotent).

Order:
  1. (optional) import synth catalog seeds — run importer separately if empty
  2. apply module_catalog HP overlay
  3. materialize HP-known catalog → modules
  4. apply module power/depth overlay(s)

Requires DATABASE_URL / backend settings. Does not invent data.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-hp-overlay", action="store_true")
    parser.add_argument("--skip-materialize", action="store_true")
    parser.add_argument("--skip-power-overlay", action="store_true")
    parser.add_argument("--power-overlay", type=Path, action="append", default=None)
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--receipt", type=Path, default=None)
    args = parser.parse_args(argv)

    sys.path.insert(0, str(REPO / "backend"))
    from core.database import SessionLocal
    from modules.catalog_routes import materialize_catalog_batch

    # Import apply helpers by path
    sys.path.insert(0, str(REPO / "scripts"))
    import apply_module_catalog_hp_overlay as hp_apply  # type: ignore
    import apply_module_power_depth_overlay as power_apply  # type: ignore

    receipt: dict = {"status": "success", "steps": []}

    if not args.skip_hp_overlay:
        r = hp_apply.main(
            [
                "--overlay",
                str(REPO / "data/synth-catalog/overlays/module-catalog-hp-v1.json"),
            ]
        )
        receipt["steps"].append({"step": "hp_overlay", "exit": r})

    if not args.skip_materialize:
        db = SessionLocal()
        try:
            batch = materialize_catalog_batch(
                db, brand=None, hp_known_only=True, limit=args.limit
            )
        finally:
            db.close()
        receipt["steps"].append({"step": "materialize_batch", "result": batch})

    if not args.skip_power_overlay:
        overlays = args.power_overlay or [
            REPO / "data/synth-catalog/overlays/module-power-depth-v1.json",
            REPO / "data/synth-catalog/overlays/module-power-depth-v2.json",
            REPO / "data/synth-catalog/overlays/module-power-depth-v3.json",
        ]
        for ov in overlays:
            ov = Path(ov)
            if not ov.is_file():
                receipt["steps"].append(
                    {"step": "power_overlay", "overlay": str(ov), "skipped": "missing"}
                )
                continue
            r = power_apply.main(["--overlay", str(ov)])
            receipt["steps"].append(
                {"step": "power_overlay", "overlay": str(ov), "exit": r}
            )

    print(json.dumps(receipt, indent=2))
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
