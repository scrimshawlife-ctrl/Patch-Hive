#!/usr/bin/env python3
"""Automate staging catalog place-loop simulation against a live API.

Steps:
  1. Health
  2. Catalog stats (HP coverage)
  3. Materialize-batch (idempotent)
  4. Create LC3-style pack on a powered case (or first Eurorack case)
  5. Compatibility dual-gate summary
  6. Overflow hard-fail probe
  7. Write receipt JSON

Env:
  PATCHHIVE_API_URL  default http://localhost:8000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def api(method: str, base: str, path: str, body: dict | None = None) -> tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        base.rstrip("/") + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:1000]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--api",
        default=os.environ.get("PATCHHIVE_API_URL", "http://localhost:8000"),
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("data/synth-catalog/receipts/simulate-catalog-place-loop.json"),
    )
    parser.add_argument("--user-id", type=int, default=1)
    parser.add_argument("--case-id", type=int, default=None)
    args = parser.parse_args(argv)
    base = args.api.rstrip("/")
    receipt: dict[str, Any] = {"status": "success", "api": base, "steps": []}

    code, health = api("GET", base, "/health")
    receipt["steps"].append({"step": "health", "code": code, "body": health})
    if code != 200:
        receipt["status"] = "failed"
        _write(args.receipt, receipt)
        return 1

    code, stats = api("GET", base, "/api/modules/catalog/stats")
    receipt["steps"].append({"step": "catalog_stats", "code": code, "body": stats})

    code, batch = api(
        "POST",
        base,
        "/api/modules/catalog/materialize-batch?limit=500&hp_known_only=true",
    )
    receipt["steps"].append(
        {
            "step": "materialize_batch",
            "code": code,
            "body": {
                k: batch.get(k)
                for k in ("status", "scanned", "created", "exists", "failed")
            }
            if isinstance(batch, dict)
            else batch,
        }
    )

    # Resolve case
    case_id = args.case_id
    if case_id is None:
        code, cases = api("GET", base, "/api/cases/?limit=100")
        rows = (cases or {}).get("cases") or []
        # Prefer LC3 (known good place-loop), then largest powered Eurorack case
        preferred = next((c for c in rows if c.get("name") == "A-100LC3"), None)
        if preferred is None:
            powered = [
                c
                for c in rows
                if (c.get("format_family") or "").lower() in ("eurorack", "")
                and c.get("power_12v_ma")
                and (c.get("total_hp") or 0) >= 84
            ]
            powered.sort(key=lambda c: c.get("total_hp") or 0, reverse=True)
            preferred = powered[0] if powered else (rows[0] if rows else None)
        case_id = preferred["id"] if preferred else None
        receipt["case_name"] = preferred.get("name") if preferred else None
    receipt["case_id"] = case_id

    # Pick small modules with known power for pack
    code, mods = api("GET", base, "/api/modules/?limit=100")
    modules = (mods or {}).get("modules") or []
    packable = [
        m
        for m in modules
        if m.get("hp")
        and m.get("hp") <= 12
        and m.get("power_12v_ma") is not None
    ]
    packable.sort(key=lambda m: m["hp"])
    placements = []
    cursor = 0
    row_hp = 84
    for m in packable[:12]:
        if cursor + m["hp"] > row_hp:
            break
        placements.append(
            {"module_id": m["id"], "row_index": 0, "start_hp": cursor}
        )
        cursor += m["hp"]
    receipt["steps"].append(
        {
            "step": "pack_plan",
            "module_count": len(placements),
            "hp_used": cursor,
        }
    )

    if case_id and placements:
        code, rack = api(
            "POST",
            base,
            "/api/racks/",
            {
                "user_id": args.user_id,
                "case_id": case_id,
                "name": "Automated place-loop simulation",
                "generation_seed": 525999,
                "tags": ["simulate", "automated"],
                "modules": placements,
            },
        )
        receipt["steps"].append(
            {
                "step": "create_rack",
                "code": code,
                "rack_id": rack.get("id") if isinstance(rack, dict) else None,
            }
        )
        if code in (200, 201) and isinstance(rack, dict) and rack.get("id"):
            rid = rack["id"]
            ccode, compat = api("GET", base, f"/api/racks/{rid}/compatibility")
            c = (compat or {}).get("compatibility") or {}
            receipt["steps"].append(
                {
                    "step": "compatibility",
                    "code": ccode,
                    "overall_status": c.get("overall_status"),
                    "physical_fit": (c.get("physical_fit") or {}).get("code"),
                    "power_headroom": [
                        {
                            "rail": r.get("rail"),
                            "status": r.get("status"),
                            "draw_ma": r.get("module_draw_ma"),
                            "capacity_ma": r.get("case_capacity_ma"),
                            "headroom_ma": r.get("headroom_ma"),
                        }
                        for r in (c.get("power_headroom") or [])
                    ],
                    "warning_codes": sorted(
                        {
                            w.get("code")
                            for w in (c.get("warnings") or [])
                            if w.get("code")
                        }
                    ),
                }
            )

            # Overflow probe
            wide = next((m for m in modules if (m.get("hp") or 0) >= 16), None)
            if wide:
                ocode, obody = api(
                    "POST",
                    base,
                    "/api/racks/",
                    {
                        "user_id": args.user_id,
                        "case_id": case_id,
                        "name": "overflow probe",
                        "generation_seed": 525998,
                        "modules": [
                            {
                                "module_id": wide["id"],
                                "row_index": 0,
                                "start_hp": 80,
                            }
                        ],
                    },
                )
                receipt["steps"].append(
                    {
                        "step": "overflow_probe",
                        "code": ocode,
                        "expect_hard_fail": ocode >= 400,
                        "detail_message": (obody.get("detail") or {}).get("message")
                        if isinstance(obody, dict)
                        else None,
                    }
                )
    else:
        receipt["steps"].append(
            {
                "step": "create_rack",
                "skipped": "no case or packable modules",
            }
        )
        receipt["status"] = "partial"

    # Validation summary
    mat = next(
        (s for s in receipt["steps"] if s.get("step") == "materialize_batch"), {}
    )
    body = mat.get("body") or {}
    receipt["validation"] = {
        "health_ok": receipt["steps"][0].get("code") == 200,
        "materialize_ok": mat.get("code") in (200, 201)
        and (body.get("failed") or 0) == 0,
        "place_ok": any(
            s.get("step") == "create_rack" and s.get("code") in (200, 201)
            for s in receipt["steps"]
        ),
        "overflow_hard_fail_ok": any(
            s.get("step") == "overflow_probe" and s.get("expect_hard_fail")
            for s in receipt["steps"]
        ),
    }
    v = receipt["validation"]
    v["all_ok"] = all(
        [
            v["health_ok"],
            v["materialize_ok"],
            v.get("place_ok", False),
        ]
    )
    if not v["all_ok"]:
        receipt["status"] = "failed"

    _write(args.receipt, receipt)
    print(json.dumps(receipt, indent=2))
    return 0 if v["all_ok"] else 1


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
