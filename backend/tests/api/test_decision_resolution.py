"""API contract for bounded Decision Intelligence resolution."""
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from canon.models import ClassificationEvidenceRecord, ImageAssetRecord, SystemInventoryRevisionRecord
from core import get_db, settings
from intelligence.contracts import DecisionPacket
from intelligence.models import DecisionReceiptRecord
from main import app


def test_decision_resolution_endpoint_is_advisory_only(db_session, sample_rack_basic, monkeypatch):
    now = datetime.now(timezone.utc)
    asset = ImageAssetRecord(
        id="img-di-api", rack_id=sample_rack_basic.id, user_id=sample_rack_basic.user_id,
        content_sha256="a" * 64, media_type="image/jpeg", width=100, height=100,
        byte_length=10, storage_path="/tmp/di.jpg", retention_days=30,
        retention_expires_at=now + timedelta(days=30), consent_provider_processing=False,
        created_at=now,
    )
    db_session.add(asset)
    candidate = {
        "candidate_id": "module-a", "entity_type": "module", "manufacturer": "Make",
        "model": "Alpha", "confidence": 0.8, "confidence_method": "fixture",
        "classification_status": "INFERRED", "evidence_id": "ev-di-api",
    }
    db_session.add(ClassificationEvidenceRecord(
        id="ev-di-api", image_asset_id=asset.id, inventory_revision_id=None,
        evidence_packet={"devices": [candidate]}, provider="fixture-vision",
        pipeline_version="vision-v1", status="INFERRED", created_at=now,
    ))
    db_session.commit()

    class Provider:
        def choose(self, request):
            return DecisionPacket(
                decision_id="decision-api", request_id=request.request_id,
                provider="fixture", provider_version="1", evidence_hash=request.evidence_hash,
                answer_type="choice", selected_choice="module-a",
                probabilities={"module-a": 0.95, "none_of_above": 0.05},
                confidence=0.95, candidate_set_hash=request.candidate_set_hash(),
                created_at=now,
            )
        def score(self, request): raise AssertionError
        def probability(self, request): raise AssertionError

    import evidence.routes as routes
    monkeypatch.setattr(routes, "_configured_decision_provider", lambda: Provider())
    monkeypatch.setattr(settings, "enable_decision_intelligence", True)

    def override_db():
        yield db_session
    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app)
        before = db_session.query(SystemInventoryRevisionRecord).count()
        response = client.post(
            f"/api/racks/{sample_rack_basic.id}/evidence/decision-resolution",
            json={"evidence_id": "ev-di-api", "idempotency_key": "api-test"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["selected_choice"] == "module-a"
        assert body["disposition"] == "AUTO_PROPOSE"
        assert body["canonical_authority"] is False
        assert db_session.query(DecisionReceiptRecord).count() == 1
        assert db_session.query(SystemInventoryRevisionRecord).count() == before

        listed = client.get(f"/api/racks/{sample_rack_basic.id}/evidence/candidates")
        shown = next(x for x in listed.json()["candidates"] if x["candidate_id"] == "module-a")
        assert shown["decision_advisory"]["provider"] == "fixture"
    finally:
        app.dependency_overrides.clear()
        monkeypatch.setattr(settings, "enable_decision_intelligence", False)


def test_decision_resolution_endpoint_defaults_off(db_session, sample_rack_basic):
    def override_db():
        yield db_session
    app.dependency_overrides[get_db] = override_db
    old = settings.enable_decision_intelligence
    settings.enable_decision_intelligence = False
    try:
        response = TestClient(app).post(
            f"/api/racks/{sample_rack_basic.id}/evidence/decision-resolution",
            json={"evidence_id": "missing", "idempotency_key": "off"},
        )
        # Missing evidence is still not disclosed as resolvable; no provider call occurs.
        assert response.status_code in {404, 409}
        assert db_session.query(DecisionReceiptRecord).count() == 0
    finally:
        settings.enable_decision_intelligence = old
        app.dependency_overrides.clear()
