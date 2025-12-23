"""
API tests for Patch Book PDF export endpoint (PAID FEATURE).

Tests the full export flow including:
- Credit gating
- Content hash generation
- Template version tracking
- Deterministic response
- Caching behavior
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from export.pdf import PATCHBOOK_TEMPLATE_VERSION, compute_patchbook_content_hash
from monetization.models import CreditsLedger, Export
from patches.models import Patch


@pytest.fixture
def sample_rack_with_run(db_session: Session, sample_rack_basic, sample_user):
    """Create a rack with an associated run."""
    from runs.models import Run

    run = Run(
        user_id=sample_user.id,
        rack_id=sample_rack_basic.id,
        config={},
        status="completed",
    )
    db_session.add(run)
    db_session.commit()
    db_session.refresh(run)
    return {"rack": sample_rack_basic, "run": run, "user": sample_user}


@pytest.fixture
def auth_token(sample_rack_with_run, db_session: Session):
    """Generate auth token for test user."""
    from community.models import User
    from core.security import create_access_token

    user = sample_rack_with_run["user"]
    return create_access_token({"sub": user.username})


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_patchbook_export_requires_authentication(sample_rack_with_run):
    """Test that patchbook export requires authentication."""
    from main import app

    client = TestClient(app)
    run_id = sample_rack_with_run["run"].id

    # No auth header
    resp = client.post(f"/api/export/runs/{run_id}/patchbook")
    assert resp.status_code in {401, 403}, "Endpoint must require authentication"


def test_patchbook_export_requires_credits(
    sample_rack_with_run, auth_token, db_session: Session
):
    """Test that patchbook export is blocked without sufficient credits."""
    from main import app

    client = TestClient(app)
    run_id = sample_rack_with_run["run"].id

    # User has 0 credits by default
    resp = client.post(
        f"/api/export/runs/{run_id}/patchbook",
        headers=_auth_headers(auth_token),
    )

    assert resp.status_code == 402, "Must return 402 Payment Required without credits"
    assert "credits" in resp.text.lower(), "Error message must mention credits"

    # Verify no export record created
    exports = db_session.query(Export).filter(Export.run_id == run_id).all()
    assert len(exports) == 0, "No export should be created when credits insufficient"


def test_patchbook_export_success_with_credits(
    sample_rack_with_run, auth_token, db_session: Session
):
    """Test successful patchbook export when user has credits."""
    from core.config import settings
    from main import app
    from monetization.models import CreditsLedger

    client = TestClient(app)
    run_id = sample_rack_with_run["run"].id
    user_id = sample_rack_with_run["user"].id

    # Grant credits
    ledger_entry = CreditsLedger(
        user_id=user_id,
        change_type="Grant",
        credits_delta=10,
        notes="Test grant",
    )
    db_session.add(ledger_entry)
    db_session.commit()

    # Request export
    resp = client.post(
        f"/api/export/runs/{run_id}/patchbook",
        headers=_auth_headers(auth_token),
    )

    assert resp.status_code == 200, f"Export should succeed: {resp.text}"

    data = resp.json()
    assert "export_id" in data, "Response must include export_id"
    assert "artifact_path" in data, "Response must include artifact_path"
    assert "content_hash" in data, "Response must include content_hash"
    assert "template_version" in data, "Response must include template_version"
    assert data["cached"] is False, "First export should not be cached"

    # Verify template version
    assert data["template_version"] == PATCHBOOK_TEMPLATE_VERSION

    # Verify PDF file exists
    pdf_path = Path(data["artifact_path"])
    assert pdf_path.exists(), f"PDF file must exist at {pdf_path}"
    assert pdf_path.stat().st_size > 5000, "PDF must have reasonable size"

    # Verify PDF starts with %PDF
    with open(pdf_path, "rb") as f:
        assert f.read(4) == b"%PDF", "File must be valid PDF"

    # Verify credits were spent
    ledger_entries = (
        db_session.query(CreditsLedger)
        .filter(CreditsLedger.user_id == user_id, CreditsLedger.change_type == "Spend")
        .all()
    )
    assert len(ledger_entries) == 1, "Exactly one spend entry should exist"
    assert ledger_entries[0].credits_delta == -settings.patchbook_export_cost

    # Verify export record created
    export_record = db_session.query(Export).filter(Export.id == data["export_id"]).first()
    assert export_record is not None, "Export record must be created"
    assert export_record.status == "completed"
    assert export_record.manifest_hash == data["content_hash"]


def test_patchbook_export_content_hash_deterministic(
    sample_rack_with_run, auth_token, db_session: Session
):
    """Test that content hash is deterministic for same rack/patches."""
    from main import app
    from monetization.models import CreditsLedger

    client = TestClient(app)
    run_id = sample_rack_with_run["run"].id
    user_id = sample_rack_with_run["user"].id
    rack_id = sample_rack_with_run["rack"].id

    # Add patches
    for i in range(3):
        patch = Patch(
            user_id=user_id,
            rack_id=rack_id,
            name=f"Patch {i}",
            category="Tonal",
            connections=[],
            generation_seed=i,
            generation_version="1.0.0",
        )
        db_session.add(patch)
    db_session.commit()

    # Get patch IDs
    patch_ids = [p.id for p in db_session.query(Patch).filter(Patch.rack_id == rack_id).all()]
    expected_hash = compute_patchbook_content_hash(rack_id, patch_ids)

    # Grant credits for two exports
    ledger_entry = CreditsLedger(
        user_id=user_id,
        change_type="Grant",
        credits_delta=20,
        notes="Test grant",
    )
    db_session.add(ledger_entry)
    db_session.commit()

    # First export
    resp1 = client.post(
        f"/api/export/runs/{run_id}/patchbook",
        headers=_auth_headers(auth_token),
    )
    assert resp1.status_code == 200
    data1 = resp1.json()

    # Verify content hash matches expected
    assert data1["content_hash"] == expected_hash, "Content hash must match computed value"

    # Second export (should be cached)
    resp2 = client.post(
        f"/api/export/runs/{run_id}/patchbook",
        headers=_auth_headers(auth_token),
    )
    assert resp2.status_code == 200
    data2 = resp2.json()

    # Verify same content hash
    assert data2["content_hash"] == data1["content_hash"], "Content hash must be consistent"
    assert data2["cached"] is True, "Second export should be cached"

    # Verify only one credit deduction
    spends = (
        db_session.query(CreditsLedger)
        .filter(CreditsLedger.user_id == user_id, CreditsLedger.change_type == "Spend")
        .all()
    )
    assert len(spends) == 1, "Only first export should consume credits"


def test_patchbook_export_caching_behavior(
    sample_rack_with_run, auth_token, db_session: Session
):
    """Test that cached exports don't consume additional credits."""
    from main import app
    from monetization.credits import get_credits_balance
    from monetization.models import CreditsLedger

    client = TestClient(app)
    run_id = sample_rack_with_run["run"].id
    user_id = sample_rack_with_run["user"].id

    # Grant exactly enough credits for one export
    ledger_entry = CreditsLedger(
        user_id=user_id,
        change_type="Grant",
        credits_delta=3,
        notes="Test grant",
    )
    db_session.add(ledger_entry)
    db_session.commit()

    initial_balance = get_credits_balance(db_session, user_id)

    # First export
    resp1 = client.post(
        f"/api/export/runs/{run_id}/patchbook",
        headers=_auth_headers(auth_token),
    )
    assert resp1.status_code == 200
    assert resp1.json()["cached"] is False

    balance_after_first = get_credits_balance(db_session, user_id)
    assert balance_after_first == 0, "Balance should be 0 after spending 3 credits"

    # Second export (cached, should not require credits)
    resp2 = client.post(
        f"/api/export/runs/{run_id}/patchbook",
        headers=_auth_headers(auth_token),
    )
    assert resp2.status_code == 200
    assert resp2.json()["cached"] is True

    balance_after_second = get_credits_balance(db_session, user_id)
    assert balance_after_second == 0, "Cached export should not consume credits"


def test_patchbook_export_returns_valid_pdf_structure(
    sample_rack_with_run, auth_token, db_session: Session
):
    """Test that exported PDF has valid structure."""
    from main import app
    from monetization.models import CreditsLedger

    client = TestClient(app)
    run_id = sample_rack_with_run["run"].id
    user_id = sample_rack_with_run["user"].id

    # Grant credits
    ledger_entry = CreditsLedger(
        user_id=user_id,
        change_type="Grant",
        credits_delta=10,
        notes="Test grant",
    )
    db_session.add(ledger_entry)
    db_session.commit()

    # Request export
    resp = client.post(
        f"/api/export/runs/{run_id}/patchbook",
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 200

    pdf_path = Path(resp.json()["artifact_path"])

    # Read PDF and verify structure
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # PDF header
    assert pdf_bytes.startswith(b"%PDF"), "Must start with PDF header"

    # PDF EOF marker
    assert b"%%EOF" in pdf_bytes, "Must contain EOF marker"

    # Template version in PDF
    pdf_str = pdf_bytes.decode("latin-1", errors="ignore")
    assert PATCHBOOK_TEMPLATE_VERSION in pdf_str, "PDF must embed template version"

    # Rack name in PDF
    rack_name = sample_rack_with_run["rack"].name
    assert rack_name in pdf_str, f"PDF must contain rack name: {rack_name}"


def test_patchbook_export_includes_patch_count_in_provenance(
    sample_rack_with_run, auth_token, db_session: Session
):
    """Test that export provenance includes patch count."""
    from main import app
    from monetization.models import CreditsLedger

    client = TestClient(app)
    run_id = sample_rack_with_run["run"].id
    user_id = sample_rack_with_run["user"].id
    rack_id = sample_rack_with_run["rack"].id

    # Add 3 patches
    for i in range(3):
        patch = Patch(
            user_id=user_id,
            rack_id=rack_id,
            name=f"Patch {i}",
            category="Tonal",
            connections=[],
            generation_seed=i,
            generation_version="1.0.0",
        )
        db_session.add(patch)
    db_session.commit()

    # Grant credits
    ledger_entry = CreditsLedger(
        user_id=user_id,
        change_type="Grant",
        credits_delta=10,
        notes="Test grant",
    )
    db_session.add(ledger_entry)
    db_session.commit()

    # Request export
    resp = client.post(
        f"/api/export/runs/{run_id}/patchbook",
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 200

    export_id = resp.json()["export_id"]

    # Check export record provenance
    export_record = db_session.query(Export).filter(Export.id == export_id).first()
    assert export_record is not None
    assert export_record.provenance is not None
    assert export_record.provenance.get("patch_count") == 3
    assert export_record.provenance.get("template_version") == PATCHBOOK_TEMPLATE_VERSION


def test_patchbook_export_404_for_missing_run(auth_token):
    """Test that export returns 404 for non-existent run."""
    from main import app

    client = TestClient(app)

    resp = client.post(
        "/api/export/runs/99999/patchbook",
        headers=_auth_headers(auth_token),
    )

    assert resp.status_code == 404
    assert "not found" in resp.text.lower()
