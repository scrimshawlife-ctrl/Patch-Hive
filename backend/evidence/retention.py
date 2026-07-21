"""Retention enforcement for image evidence assets."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from canon.models import ImageAssetRecord


def expire_image_assets(db: Session, *, now: datetime | None = None) -> dict[str, int]:
    """Soft-delete assets past retention_expires_at; purge orphan storage files.

    Returns counts for observability receipts.
    """
    instant = now or datetime.now(timezone.utc)
    expired = (
        db.query(ImageAssetRecord)
        .filter(
            ImageAssetRecord.deleted_at.is_(None),
            ImageAssetRecord.retention_expires_at <= instant,
        )
        .all()
    )
    soft_deleted = 0
    purged_files = 0
    for record in expired:
        record.deleted_at = instant
        soft_deleted += 1
        path = Path(str(record.storage_path))
        live_siblings = (
            db.query(ImageAssetRecord)
            .filter(
                ImageAssetRecord.content_sha256 == record.content_sha256,
                ImageAssetRecord.deleted_at.is_(None),
                ImageAssetRecord.id != record.id,
            )
            .count()
        )
        if live_siblings == 0 and path.exists():
            try:
                os.remove(path)
                purged_files += 1
            except OSError:
                pass
    if soft_deleted:
        db.flush()
    return {"soft_deleted": soft_deleted, "purged_files": purged_files}
