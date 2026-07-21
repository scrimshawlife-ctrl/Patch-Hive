"""Compatibility shim — prefer ``canon.gallery_revisions`` for new code."""

from __future__ import annotations

from canon.gallery_revisions import GalleryRevision, append_revision

__all__ = ["GalleryRevision", "append_revision"]
