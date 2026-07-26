#!/usr/bin/env python3
"""API walkthrough: Design Engine preview + inline-fulfilled export on staging.

Prerequisites:
  - Compose stack with design-engine overlay (flags on)
  - Host Python with backend deps (backend/.venv-acceptance is fine)

Usage (repo root):
  set DATABASE_URL=postgresql://patchhive:…@localhost:5433/patchhive
  set STAGING_API_URL=http://localhost:18000
  set PYTHONPATH=backend
  python scripts/staging/design_engine_walkthrough.py
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import uuid
from pathlib import Path

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Register SQLAlchemy relationships used by User / ledger / exports (same as main.py).
from account.models import CreditLedgerEntry, ExportRecord  # noqa: E402, F401
from canon.models import CanonicalCreditLedgerEntryRecord, CanonicalExportRecord  # noqa: E402, F401
from community.models import User  # noqa: E402
from core.security import get_password_hash  # noqa: E402
from monetization.models import CreditsLedger  # noqa: E402, F401
from runs.bridge import ensure_legacy_run_export_bridge  # noqa: E402
from runs.models import Run  # noqa: E402


def _load_seed_module():
    path = REPO_ROOT / "scripts" / "seed_golden_demo.py"
    spec = importlib.util.spec_from_file_location("seed_golden_demo", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["seed_golden_demo"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    api = os.environ.get("STAGING_API_URL", "http://localhost:18000").rstrip("/")
    db_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://patchhive:staging-smoke-db-pass-xx@localhost:5433/patchhive",
    )
    print(f"API={api}")
    print(f"DATABASE_URL host={db_url.split('@')[-1]}")

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    seed_mod = _load_seed_module()

    print("=== Seed golden demo ===")
    seed = seed_mod.seed_golden_demo(db)
    print(f"  user={seed.username} run_id={seed.run_id} patches={seed.patch_count}")

    admin = db.query(User).filter(User.username == "admin_demo").first()
    if admin is None:
        admin = User(
            username="admin_demo",
            email="admin_demo@example.com",
            password_hash=get_password_hash("admin-pass"),
            display_name="admin_demo",
            role="Admin",
            referral_code="admin_demo-ref",
        )
        db.add(admin)
    else:
        admin.role = "Admin"
        admin.password_hash = get_password_hash("admin-pass")
    db.commit()
    print("  admin ready (admin_demo / admin-pass)")

    run = db.get(Run, seed.run_id)
    assert run is not None
    bridge = ensure_legacy_run_export_bridge(db, run)
    db.commit()
    sources = bridge.as_export_body_fields()
    print(f"  bridge ready={bridge.export_bridge_ready}")
    db.close()

    client = httpx.Client(base_url=api, timeout=90.0)

    def login(username: str, password: str) -> str:
        r = client.post(
            "/api/community/auth/login",
            json={"username": username, "password": password},
        )
        r.raise_for_status()
        return r.json()["access_token"]

    print("=== Login demo user ===")
    token = login(seed.username, seed.password)
    headers = {"Authorization": f"Bearer {token}"}

    print("=== POST /api/canon/exports/preview (free) ===")
    preview_body = {
        "source_run_id": sources["source_run_id"],
        "source_rig_revision_id": sources["source_rig_revision_id"],
        "artifact_manifest_hash": sources["artifact_manifest_hash"],
        "max_pages": 3,
    }
    prev = client.post("/api/canon/exports/preview", headers=headers, json=preview_body)
    if prev.status_code != 200:
        print(f"FAIL preview {prev.status_code}: {prev.text}")
        return 1
    prev_data = prev.json()
    if not prev_data.get("style_recipe_hash"):
        print(f"FAIL preview missing style_recipe_hash: {prev_data}")
        return 1
    print(
        f"  style_recipe_hash={str(prev_data['style_recipe_hash'])[:16]}… "
        f"pages={len(prev_data.get('page_summaries') or [])} "
        f"load_path={prev_data.get('load_path')}"
    )

    print("=== POST /api/canon/style-recipes ===")
    recipe_name = f"staging-walkthrough-{uuid.uuid4().hex[:8]}"
    cr = client.post(
        "/api/canon/style-recipes",
        headers=headers,
        json={"name": recipe_name, "notes": "design engine staging", "style_recipe": {}},
    )
    style_recipe_id = None
    if cr.status_code in (200, 201):
        style_recipe_id = cr.json()["id"]
        print(f"  recipe_id={style_recipe_id}")
    else:
        print(f"  WARN style-recipes {cr.status_code}: {cr.text[:200]}")

    print("=== Admin grant credits ===")
    admin_token = login("admin_demo", "admin-pass")
    grant = client.post(
        f"/api/admin/users/{seed.user_id}/credits/grant",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"credits": 10, "reason": "design-engine-staging-walkthrough"},
    )
    if grant.status_code not in (200, 201):
        print(f"FAIL grant {grant.status_code}: {grant.text}")
        return 1
    print(f"  grant={grant.json().get('status')}")

    print("=== POST /api/canon/exports (debit + inline fulfill) ===")
    export_body = {
        "source_run_id": sources["source_run_id"],
        "source_rig_revision_id": sources["source_rig_revision_id"],
        "artifact_manifest_hash": sources["artifact_manifest_hash"],
        "formats": ["pdf", "json"],
        "license": "personal",
        "idempotency_key": f"design-walk-{uuid.uuid4().hex}",
    }
    if style_recipe_id:
        export_body["style_recipe_id"] = style_recipe_id
    else:
        export_body["style_recipe"] = {}

    ex = client.post("/api/canon/exports", headers=headers, json=export_body)
    print(f"  export HTTP {ex.status_code}: {ex.text[:800]}")
    if ex.status_code not in (200, 201):
        print(f"FAIL export {ex.status_code}: {ex.text}")
        return 1
    export = ex.json()
    # Response may nest under "export" or use export_id
    if "id" not in export and isinstance(export.get("export"), dict):
        export = export["export"]
    export_id = export.get("id") or export.get("export_id")
    if not export_id:
        print(f"FAIL export response missing id: {export}")
        return 1
    status = export.get("status")
    print(f"  export_id={export_id} status={status}")
    if status != "succeeded":
        g = client.get(f"/api/canon/exports/{export_id}", headers=headers)
        print(f"  get export HTTP {g.status_code}: {g.text[:500]}")
        g.raise_for_status()
        export = g.json()
        if "id" not in export and isinstance(export.get("export"), dict):
            export = export["export"]
        status = export.get("status")
        print(f"  polled status={status}")
    if status != "succeeded":
        print(f"FAIL expected status=succeeded got {status}")
        print(json.dumps(export, indent=2)[:1000])
        return 1

    print("=== Pack files in container ===")
    # Best-effort: caller can check via compose exec
    print(f"  export_id for pack dir: {export_id}")
    print("WALKTHROUGH PASS")
    print(
        json.dumps(
            {
                "export_id": export_id,
                "status": status,
                "style_recipe_id": style_recipe_id,
                "pack_manifest_hash": export.get("pack_manifest_hash"),
                "composition_hash": export.get("composition_hash"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
