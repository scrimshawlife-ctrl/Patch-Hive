"""Ranked candidates + confirmation → inventory revision API."""

from __future__ import annotations

import io

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.orm import Session

from canon.models import SystemInventoryRevisionRecord
from main import app
from racks.models import Rack


def _client(db_session: Session) -> TestClient:
    from core import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (128, 96), (11, 22, 33)).save(buf, format="JPEG")
    return buf.getvalue()


def test_list_and_confirm_candidates(
    db_session: Session, sample_rack_basic: Rack, tmp_path
) -> None:
    from core import settings

    settings.export_dir = str(tmp_path)
    client = _client(db_session)

    upload = client.post(
        f"/api/racks/{sample_rack_basic.id}/evidence/images",
        files=[("files", ("rig.jpg", _jpeg_bytes(), "image/jpeg"))],
        data={"run_vision_mock": "true", "retention_days": "30"},
    )
    assert upload.status_code == 201, upload.text
    assert upload.json()["uploaded"]

    listed = client.get(f"/api/racks/{sample_rack_basic.id}/evidence/candidates")
    assert listed.status_code == 200, listed.text
    body = listed.json()
    assert body["total"] >= 1
    candidates = body["candidates"]
    # Ranked by confidence desc
    confidences = [c["confidence"] for c in candidates]
    assert confidences == sorted(confidences, reverse=True)

    top = candidates[0]
    confirm = client.post(
        f"/api/racks/{sample_rack_basic.id}/evidence/confirmations",
        json={
            "confirmed_by": "tester",
            "decisions": [
                {
                    "candidate_id": top["candidate_id"],
                    "status": "confirm",
                    "module_revision_id": "catalog-module-test-vco",
                },
                *[{"candidate_id": c["candidate_id"], "status": "reject"} for c in candidates[1:]],
            ],
        },
    )
    assert confirm.status_code == 201, confirm.text
    result = confirm.json()
    assert result["confirmed_count"] == 1
    assert result["ready_for_generation"] is True
    assert result["inventory_revision_id"].startswith("inv-rev-")
    assert db_session.get(SystemInventoryRevisionRecord, result["inventory_revision_id"])

    # Confirm without module revision fails closed
    bad = client.post(
        f"/api/racks/{sample_rack_basic.id}/evidence/confirmations",
        json={
            "decisions": [
                {"candidate_id": top["candidate_id"], "status": "confirm"},
            ]
        },
    )
    assert bad.status_code == 400
    assert "MODULE_REVISION_REQUIRED" in bad.text

    inv_list = client.get(f"/api/racks/{sample_rack_basic.id}/evidence/inventory")
    assert inv_list.status_code == 200, inv_list.text
    inv_body = inv_list.json()
    assert inv_body["total"] >= 1
    assert inv_body["latest"]["inventory_revision_id"] == result["inventory_revision_id"]
    assert inv_body["latest"]["ready_for_generation"] is True
    assert inv_body["latest"]["confirmed_count"] == 1

    app.dependency_overrides.clear()
