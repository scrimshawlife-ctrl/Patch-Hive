from __future__ import annotations

from datetime import datetime, timezone

from patchhive.gallery.store import ModuleGalleryStore
from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    GalleryImageRef,
    ModuleGalleryEntry,
    Provenance,
    ProvenanceType,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def attach_module_image_append_only(
    store: ModuleGalleryStore,
    *,
    module_gallery_id: str,
    image_url: str,
    kind: str = "manual_upload",
    evidence_ref: str,
) -> ModuleGalleryEntry:
    """
    Append a new revision to ModuleGalleryEntry adding an image ref.
    """
    latest = store.get_latest(module_gallery_id)
    if latest is None:
        raise ValueError(f"Module not found in gallery: {module_gallery_id}")

    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=_now_utc(),
                evidence_ref=evidence_ref,
                method="attach_module_image_append_only",
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )

    img = GalleryImageRef(url=image_url, kind=kind, meta=meta)
    updated = latest.model_copy(
        update={
            "rev": _now_utc(),
            "images": list(latest.images) + [img],
        }
    )
    store.append_revision(updated)
    return updated
