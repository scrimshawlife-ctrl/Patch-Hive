from __future__ import annotations

from patchhive.schemas_library import LibraryConstraints, LibraryTier


def starter_preset() -> LibraryConstraints:
    return LibraryConstraints(tier=LibraryTier.starter, max_cables=8, allow_feedback=False)


def core_preset() -> LibraryConstraints:
    return LibraryConstraints(tier=LibraryTier.core, max_cables=12, allow_feedback=False)


def deep_preset() -> LibraryConstraints:
    return LibraryConstraints(tier=LibraryTier.deep, max_cables=16, allow_feedback=True)
