"""HTTP surface for the canonical export/download/webhook boundary.

These routes intentionally wrap pure domain functions in ``canon.exports`` and
``canon.downloads``. Legacy ``/api/export`` PatchBook routes remain for the
current product path; this router is the canonical contract entrypoint.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from canon.contracts import ExportRequest
from canon.downloads import DownloadTokenError, issue_download_token, verify_download_token
from canon.exports import (
    ExportBoundaryError,
    credit_balance,
    request_export,
    verify_stripe_webhook,
)
from canon.models import CanonicalExportRecord, StripeEventRecordModel
from community.auth import require_auth
from community.models import User
from core import get_db, settings

router = APIRouter()

ExportFormat = Literal["pdf", "svg", "json", "zip"]


class CanonicalExportCreate(BaseModel):
    source_run_id: str = Field(..., min_length=1, max_length=64)
    source_rig_revision_id: str = Field(..., min_length=1, max_length=64)
    artifact_manifest_hash: str = Field(..., min_length=64, max_length=64)
    formats: list[ExportFormat] = Field(default_factory=lambda: ["pdf", "json"])
    license: str = Field(default="personal", min_length=1, max_length=100)
    credit_cost: int | None = Field(default=None, ge=0)
    idempotency_key: str = Field(..., min_length=8, max_length=128)


class CanonicalExportResponse(BaseModel):
    export_id: str
    status: str
    credit_cost: int
    ledger_entry_id: str | None
    source_run_id: str
    source_rig_revision_id: str
    idempotency_key: str
    created_at: datetime


class DownloadTokenCreate(BaseModel):
    ttl_seconds: int = Field(default=300, ge=1, le=15 * 60)


class DownloadTokenResponse(BaseModel):
    export_id: str
    token: str
    ttl_seconds: int


class DownloadVerifyRequest(BaseModel):
    token: str
    user_id: int | None = None


class DownloadVerifyResponse(BaseModel):
    export_id: str
    user_id: str
    expires_at: int
    status: str


class CreditBalanceResponse(BaseModel):
    balance: int


class StripeWebhookResponse(BaseModel):
    stripe_event_id: str
    status: str
    event_type: str
    duplicate: bool


def _download_secret() -> str:
    secret = (settings.download_token_secret or settings.secret_key or "").strip()
    if len(secret.encode("utf-8")) < 32:
        # Deterministic pad for local/dev only; production policy rejects weak secrets.
        secret = (secret + ("0" * 32))[:32]
    return secret


def _export_response(record: CanonicalExportRecord) -> CanonicalExportResponse:
    return CanonicalExportResponse(
        export_id=record.id,
        status=record.status,
        credit_cost=record.credit_cost,
        ledger_entry_id=record.ledger_entry_id,
        source_run_id=record.source_run_id,
        source_rig_revision_id=record.source_rig_revision_id,
        idempotency_key=record.idempotency_key,
        created_at=record.created_at,
    )


@router.get("/credits/balance", response_model=CreditBalanceResponse)
def get_canonical_credit_balance(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> CreditBalanceResponse:
    return CreditBalanceResponse(balance=credit_balance(db, current_user.id))


@router.post("/exports", response_model=CanonicalExportResponse, status_code=201)
def create_canonical_export(
    body: CanonicalExportCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> CanonicalExportResponse:
    if not body.formats:
        raise HTTPException(status_code=400, detail="At least one export format is required")

    cost = settings.patchbook_export_cost if body.credit_cost is None else body.credit_cost
    request_id = hashlib.sha256(
        f"{current_user.id}:{body.idempotency_key}".encode("utf-8")
    ).hexdigest()[:32]
    domain_request = ExportRequest(
        request_id=request_id,
        user_id=current_user.id,
        source_run_id=body.source_run_id,
        source_rig_revision_id=body.source_rig_revision_id,
        formats=tuple(body.formats),
        license=body.license,
        credit_cost=cost,
        idempotency_key=body.idempotency_key,
        requested_at=datetime.now(timezone.utc),
    )
    try:
        export = request_export(
            db,
            domain_request,
            artifact_manifest_hash=body.artifact_manifest_hash,
            export_version=settings.patch_engine_version,
        )
        db.commit()
        db.refresh(export)
    except ExportBoundaryError as exc:
        db.rollback()
        code = str(exc)
        if code == "INSUFFICIENT_CREDITS":
            raise HTTPException(status_code=402, detail=code) from exc
        raise HTTPException(status_code=400, detail=code) from exc
    except Exception:
        db.rollback()
        raise

    return _export_response(export)


@router.get("/exports/{export_id}", response_model=CanonicalExportResponse)
def get_canonical_export(
    export_id: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> CanonicalExportResponse:
    export = db.get(CanonicalExportRecord, export_id)
    if export is None or export.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Export not found")
    return _export_response(export)


@router.post(
    "/exports/{export_id}/download-token",
    response_model=DownloadTokenResponse,
)
def create_download_token(
    export_id: str,
    body: DownloadTokenCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> DownloadTokenResponse:
    export = db.get(CanonicalExportRecord, export_id)
    if export is None or export.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Export not found")
    if export.status not in {"queued", "running", "succeeded"}:
        raise HTTPException(status_code=409, detail="Export is not downloadable")

    try:
        token = issue_download_token(
            export_id=export.id,
            user_id=str(current_user.id),
            secret=_download_secret(),
            ttl_seconds=body.ttl_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DownloadTokenResponse(
        export_id=export.id,
        token=token,
        ttl_seconds=body.ttl_seconds,
    )


@router.post(
    "/exports/{export_id}/download",
    response_model=DownloadVerifyResponse,
)
def verify_download(
    export_id: str,
    body: DownloadVerifyRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
) -> DownloadVerifyResponse:
    export = db.get(CanonicalExportRecord, export_id)
    if export is None or export.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Export not found")

    try:
        grant = verify_download_token(
            body.token,
            export_id=export.id,
            user_id=str(current_user.id),
            secret=_download_secret(),
        )
    except DownloadTokenError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return DownloadVerifyResponse(
        export_id=grant.export_id,
        user_id=grant.user_id,
        expires_at=grant.expires_at,
        status=export.status,
    )


@router.post("/webhooks/stripe", response_model=StripeWebhookResponse)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
) -> StripeWebhookResponse:
    """Replay-safe Stripe-style webhook intake (test-mode by default)."""

    if settings.environment.lower() == "production" and not settings.allow_production_payments:
        # Hard reject production payment intake while the kill switch is off.
        raise HTTPException(status_code=403, detail="PRODUCTION_PAYMENTS_DISABLED")

    secret = (settings.stripe_webhook_secret or "").strip()
    if not secret:
        # Development convenience: derive a stable local secret only outside production.
        if settings.environment.lower() == "production":
            raise HTTPException(status_code=503, detail="STRIPE_WEBHOOK_SECRET is not configured")
        secret = (settings.secret_key + "stripe-dev").ljust(32, "0")[:64]

    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body()
    try:
        provisional_id = ""
        try:
            provisional_id = str(json.loads(payload).get("id") or "")
        except (json.JSONDecodeError, TypeError, AttributeError):
            provisional_id = ""
        already_seen = bool(
            provisional_id and db.get(StripeEventRecordModel, provisional_id) is not None
        )
        record, event = verify_stripe_webhook(
            db,
            payload=payload,
            signature_header=stripe_signature,
            secret=secret,
            test_mode=settings.stripe_test_mode,
        )
        db.commit()
        db.refresh(record)
    except ExportBoundaryError as exc:
        db.rollback()
        code = str(exc)
        status = 400
        if code in {"LIVEMODE_EVENT_REJECTED", "WEBHOOK_REPLAY_CONFLICT"}:
            status = 409
        raise HTTPException(status_code=status, detail=code) from exc
    except Exception:
        db.rollback()
        raise

    return StripeWebhookResponse(
        stripe_event_id=record.stripe_event_id,
        status=record.status,
        event_type=str(event.get("type", record.event_type)),
        duplicate=already_seen,
    )


def validate_payment_startup_policy(app_settings: Any = settings) -> None:
    """Fail closed when production payment configuration is unsafe."""

    env = str(getattr(app_settings, "environment", "development")).lower()
    if env != "production":
        return

    allow = bool(getattr(app_settings, "allow_production_payments", False))
    test_mode = bool(getattr(app_settings, "stripe_test_mode", True))
    webhook_secret = str(getattr(app_settings, "stripe_webhook_secret", "") or "").strip()
    download_secret = str(
        getattr(app_settings, "download_token_secret", "")
        or getattr(app_settings, "secret_key", "")
    ).strip()

    if not allow:
        if not test_mode:
            raise RuntimeError(
                "Production requires STRIPE_TEST_MODE=true while ALLOW_PRODUCTION_PAYMENTS=false"
            )
        return

    # Production payments explicitly enabled: require reviewed secrets.
    if test_mode:
        raise RuntimeError(
            "ALLOW_PRODUCTION_PAYMENTS=true is incompatible with STRIPE_TEST_MODE=true"
        )
    if len(webhook_secret) < 16:
        raise RuntimeError("ALLOW_PRODUCTION_PAYMENTS requires a real STRIPE_WEBHOOK_SECRET")
    if len(download_secret.encode("utf-8")) < 32:
        raise RuntimeError(
            "ALLOW_PRODUCTION_PAYMENTS requires DOWNLOAD_TOKEN_SECRET or SECRET_KEY >= 32 bytes"
        )
