"""Multi-image evidence upload, listing, and retention-aware deletion."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from canon.models import ClassificationEvidenceRecord, ImageAssetRecord
from core import get_db, settings
from evidence.images import (
    SignatureImageScanner,
    UnsafeImageError,
    assess_local_image_quality,
    prepare_image_evidence,
)
from evidence.vision_provider import (
    MockDeterministicVisionProvider,
    VisionProviderContext,
    collect_evidence_packet,
)
from racks.models import Rack

router = APIRouter()

DEFAULT_RETENTION_DAYS = 30
MAX_FILES_PER_REQUEST = 12


class ImageAssetResponse(BaseModel):
    id: str
    rack_id: int
    content_sha256: str
    media_type: str
    width: int
    height: int
    byte_length: int
    retention_days: int
    retention_expires_at: datetime
    consent_provider_processing: bool
    deleted_at: datetime | None = None
    created_at: datetime
    quality_accepted: bool | None = None
    evidence_status: str | None = None


class ImageAssetListResponse(BaseModel):
    total: int
    assets: list[ImageAssetResponse]


class MultiImageUploadResponse(BaseModel):
    uploaded: list[ImageAssetResponse]
    rejected: list[dict[str, str]] = Field(default_factory=list)


def _evidence_root() -> Path:
    root = Path(settings.export_dir) / "evidence"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _asset_response(
    record: ImageAssetRecord,
    *,
    quality_accepted: bool | None = None,
    evidence_status: str | None = None,
) -> ImageAssetResponse:
    return ImageAssetResponse(
        id=str(record.id),
        rack_id=int(record.rack_id),
        content_sha256=str(record.content_sha256),
        media_type=str(record.media_type),
        width=int(record.width),
        height=int(record.height),
        byte_length=int(record.byte_length),
        retention_days=int(record.retention_days),
        retention_expires_at=record.retention_expires_at,
        consent_provider_processing=bool(record.consent_provider_processing),
        deleted_at=record.deleted_at,
        created_at=record.created_at,
        quality_accepted=quality_accepted,
        evidence_status=evidence_status,
    )


@router.post(
    "/racks/{rack_id}/evidence/images",
    response_model=MultiImageUploadResponse,
    status_code=201,
)
async def upload_rack_evidence_images(
    rack_id: int,
    files: list[UploadFile] = File(...),
    retention_days: int = Form(DEFAULT_RETENTION_DAYS),
    consent_provider_processing: bool = Form(False),
    run_vision_mock: bool = Form(True),
    db: Session = Depends(get_db),
) -> MultiImageUploadResponse:
    """Upload one or more images as untrusted evidence for a rack.

    Images are re-encoded and metadata-stripped. Provider processing consent is
    recorded; live cloud providers are not invoked — mock evidence only.
    """
    rack = db.get(Rack, rack_id)
    if rack is None:
        raise HTTPException(status_code=404, detail="Rack not found")
    if not files:
        raise HTTPException(status_code=400, detail="NO_FILES")
    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(status_code=400, detail="TOO_MANY_FILES")
    if retention_days < 1 or retention_days > 365:
        raise HTTPException(status_code=400, detail="RETENTION_DAYS_INVALID")

    uploaded: list[ImageAssetResponse] = []
    rejected: list[dict[str, str]] = []
    scanner = SignatureImageScanner()
    provider = MockDeterministicVisionProvider()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=retention_days)
    user_id = int(rack.user_id)  # type: ignore[arg-type]

    for upload in files:
        filename = upload.filename or "upload"
        try:
            raw = await upload.read()
            prepared = prepare_image_evidence(
                raw,
                declared_media_type=upload.content_type,
                scanner=scanner,
            )
            quality = assess_local_image_quality(prepared)
            if not quality.accepted:
                rejected.append(
                    {
                        "filename": filename,
                        "reason": quality.reasons[0] if quality.reasons else "QUALITY_REJECTED",
                    }
                )
                continue

            asset_id = f"img-{uuid.uuid4().hex[:20]}"
            storage_name = f"{prepared.sha256}.jpg"
            storage_path = _evidence_root() / storage_name
            if not storage_path.exists():
                storage_path.write_bytes(prepared.content)

            record = ImageAssetRecord(
                id=asset_id,
                rack_id=rack_id,
                user_id=user_id,
                content_sha256=prepared.sha256,
                media_type=prepared.media_type,
                width=prepared.width,
                height=prepared.height,
                byte_length=len(prepared.content),
                storage_path=str(storage_path),
                retention_days=retention_days,
                retention_expires_at=expires,
                consent_provider_processing=consent_provider_processing,
                created_at=now,
            )
            db.add(record)
            db.flush()

            evidence_status = None
            if run_vision_mock:
                packet = collect_evidence_packet(
                    provider,
                    VisionProviderContext(
                        image_asset_id=asset_id,
                        image_bytes=prepared.content,
                        request_id=f"req-{asset_id}",
                    ),
                )
                evidence_status = str(packet.get("status"))
                db.add(
                    ClassificationEvidenceRecord(
                        id=f"ev-{uuid.uuid4().hex[:20]}",
                        image_asset_id=asset_id,
                        inventory_revision_id=None,
                        evidence_packet=packet,
                        provider=provider.provider_name,
                        pipeline_version=str(
                            packet.get("pipeline_version") or "vision-evidence.v1"
                        ),
                        status=evidence_status or "INFERRED",
                        created_at=now,
                    )
                )
                db.flush()

            uploaded.append(
                _asset_response(
                    record,
                    quality_accepted=True,
                    evidence_status=evidence_status,
                )
            )
        except UnsafeImageError as exc:
            rejected.append({"filename": filename, "reason": str(exc)})
        except Exception as exc:  # pragma: no cover - defensive
            rejected.append({"filename": filename, "reason": f"UPLOAD_FAILED:{type(exc).__name__}"})

    db.commit()
    return MultiImageUploadResponse(uploaded=uploaded, rejected=rejected)


@router.get("/racks/{rack_id}/evidence/images", response_model=ImageAssetListResponse)
def list_rack_evidence_images(
    rack_id: int,
    include_deleted: bool = False,
    db: Session = Depends(get_db),
) -> ImageAssetListResponse:
    rack = db.get(Rack, rack_id)
    if rack is None:
        raise HTTPException(status_code=404, detail="Rack not found")
    query = db.query(ImageAssetRecord).filter(ImageAssetRecord.rack_id == rack_id)
    if not include_deleted:
        query = query.filter(ImageAssetRecord.deleted_at.is_(None))
    rows = query.order_by(ImageAssetRecord.created_at.desc()).all()
    return ImageAssetListResponse(
        total=len(rows),
        assets=[_asset_response(row) for row in rows],
    )


@router.delete("/racks/{rack_id}/evidence/images/{asset_id}", status_code=200)
def delete_rack_evidence_image(
    rack_id: int,
    asset_id: str,
    purge_bytes: bool = False,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Soft-delete image evidence. Optionally purge storage bytes.

    Classification evidence and inventory lineage remain for audit when
    ``purge_bytes`` is false; storage files are removed when true and no other
    non-deleted asset shares the same content hash.
    """
    record = (
        db.query(ImageAssetRecord)
        .filter(ImageAssetRecord.id == asset_id, ImageAssetRecord.rack_id == rack_id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Image asset not found")
    if record.deleted_at is None:
        record.deleted_at = datetime.now(timezone.utc)
        db.flush()

    if purge_bytes:
        path = Path(str(record.storage_path))
        siblings = (
            db.query(ImageAssetRecord)
            .filter(
                ImageAssetRecord.content_sha256 == record.content_sha256,
                ImageAssetRecord.deleted_at.is_(None),
            )
            .count()
        )
        if siblings == 0 and path.exists():
            try:
                os.remove(path)
            except OSError:
                pass

    db.commit()
    return {"status": "deleted", "asset_id": asset_id}
