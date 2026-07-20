import hashlib
import hmac
import json
from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from canon.contracts import ExportRequest
from canon.exports import (
    ExportBoundaryError,
    compensate_failed_export,
    credit_balance,
    reconcile_ledger,
    request_export,
    verify_stripe_webhook,
)
from canon.models import CanonicalCreditLedgerEntryRecord
from tests.unit.test_canon_contracts import _persist_hierarchy

NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _request(user_id: int) -> ExportRequest:
    return ExportRequest(
        request_id="request-1",
        user_id=user_id,
        source_run_id="run-1",
        source_rig_revision_id="rig-rev-1",
        formats=("pdf", "json"),
        license="personal",
        credit_cost=3,
        idempotency_key="idem-1",
        requested_at=NOW,
    )


def test_export_retry_debits_once_and_failure_reverses_once(db_session: Session) -> None:
    user, _patch = _persist_hierarchy(db_session)
    db_session.add(
        CanonicalCreditLedgerEntryRecord(
            id="grant-1",
            user_id=user.id,
            delta=10,
            entry_type="grant",
            idempotency_key="grant-1",
            created_at=NOW,
        )
    )
    db_session.commit()
    first = request_export(
        db_session,
        _request(user.id),
        artifact_manifest_hash="a" * 64,
        export_version="1.0.0",
    )
    second = request_export(
        db_session,
        _request(user.id),
        artifact_manifest_hash="a" * 64,
        export_version="1.0.0",
    )
    assert first.id == second.id
    assert credit_balance(db_session, user.id) == 7
    compensate_failed_export(db_session, first, occurred_at=NOW)
    compensate_failed_export(db_session, first, occurred_at=NOW)
    assert credit_balance(db_session, user.id) == 10
    report = reconcile_ledger(db_session, user.id)
    assert report.anomalies == ()
    assert report.export_debits == report.reversals == 3


def test_insufficient_credit_does_not_create_export(db_session: Session) -> None:
    user, _patch = _persist_hierarchy(db_session)
    with pytest.raises(ExportBoundaryError, match="INSUFFICIENT_CREDITS"):
        request_export(
            db_session,
            _request(user.id),
            artifact_manifest_hash="a" * 64,
            export_version="1.0.0",
        )


def _signature(payload: bytes, secret: str, timestamp: int) -> str:
    digest = hmac.new(
        secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={digest}"


def test_stripe_signature_replay_and_livemode_gate(db_session: Session) -> None:
    timestamp = 1_700_000_000
    payload = json.dumps(
        {"id": "evt_1", "type": "payment_intent.succeeded", "livemode": False}
    ).encode()
    signature = _signature(payload, "whsec_test", timestamp)
    first, _event = verify_stripe_webhook(
        db_session,
        payload=payload,
        signature_header=signature,
        secret="whsec_test",
        now=timestamp,
    )
    second, _event = verify_stripe_webhook(
        db_session,
        payload=payload,
        signature_header=signature,
        secret="whsec_test",
        now=timestamp,
    )
    assert first.stripe_event_id == second.stripe_event_id

    live = json.dumps({"id": "evt_live", "type": "charge.succeeded", "livemode": True}).encode()
    with pytest.raises(ExportBoundaryError, match="LIVEMODE_EVENT_REJECTED"):
        verify_stripe_webhook(
            db_session,
            payload=live,
            signature_header=_signature(live, "whsec_test", timestamp),
            secret="whsec_test",
            now=timestamp,
        )
