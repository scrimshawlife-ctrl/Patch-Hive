from __future__ import annotations

from typing import Callable, Dict

from patchhive.pipeline.e2e_config import E2EConfig
from patchhive.pipeline.run_e2e import run_e2e
from patchhive.vision.gemini_interface import GeminiVisionClient


ProgressFn = Callable[[str, float], None]  # (stage, progress)


def run_e2e_with_progress(
    *,
    image_ref: str,
    rig_id: str,
    config: E2EConfig,
    gemini: GeminiVisionClient,
    on_progress: ProgressFn,
) -> Dict:
    """
    Same work as run_e2e(), but reports coarse progress stages.
    """
    on_progress("vision_extract", 0.10)
    # run_e2e calls gemini inside; we can only report coarse stages here.
    # If you want finer granularity, break run_e2e into sub-ops and call on_progress between them.
    on_progress("vision_to_rigspec", 0.25)
    on_progress("canonicalize_rig", 0.35)
    on_progress("layout_suggest", 0.45)
    on_progress("generate_library", 0.60)
    on_progress("prune_library", 0.72)
    on_progress("render_export", 0.90)

    out = run_e2e(image_ref=image_ref, rig_id=rig_id, config=config, gemini=gemini)

    on_progress("done", 1.00)
    return out
