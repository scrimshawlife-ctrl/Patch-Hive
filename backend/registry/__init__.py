"""
Device Registry package (canonical product database backing).

See:
- docs/DEVICE_REGISTRY.md
- docs/PRODUCT_DATABASE_COMPLETENESS_ROADMAP.md
- docs/adr/ADR-006-public-product-database.md
- backend/registry/models.py (stub)
- Issue #68

Transition plan: adapters + migrations from ModuleCatalog / GalleryRevision / legacy gallery.
"""

from .models import *  # noqa: F401,F403  # will export when stable
