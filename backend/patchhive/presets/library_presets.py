from __future__ import annotations

from patchhive.schemas_library import PatchSpaceConstraints, PatchTier


def starter_preset() -> PatchSpaceConstraints:
    return PatchSpaceConstraints(
        tier=PatchTier.starter,
        max_cables=4,
        allow_feedback=False,
        require_output_path=True,
        max_candidates_per_template=600,
        keep_top_per_template=12,
    )


def core_preset() -> PatchSpaceConstraints:
    return PatchSpaceConstraints(
        tier=PatchTier.core,
        max_cables=6,
        allow_feedback=False,
        require_output_path=True,
        max_candidates_per_template=2000,
        keep_top_per_template=35,
    )


def deep_preset() -> PatchSpaceConstraints:
    return PatchSpaceConstraints(
        tier=PatchTier.deep,
        max_cables=10,
        allow_feedback=True,  # still validator-flags runaway
        require_output_path=True,
        max_candidates_per_template=5000,
        keep_top_per_template=80,
    )
