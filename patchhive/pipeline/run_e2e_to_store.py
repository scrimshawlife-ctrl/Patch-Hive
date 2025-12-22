from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from patchhive.pipeline.e2e_config import E2EConfig
from patchhive.pipeline.run_e2e import run_e2e
from patchhive.store.artifact_store import ArtifactStore, ArtifactRefs
from patchhive.vision.gemini_interface import GeminiVisionClient


def run_e2e_to_store(
    *,
    store: ArtifactStore,
    gemini: GeminiVisionClient,
    rig_id: str,
    image_ref: str,
    cfg: E2EConfig,
) -> Dict:
    refs = store.alloc_run(rig_id=rig_id, image_ref=image_ref, preset=cfg.preset)
    store.write_input(refs, {"rig_id": rig_id, "image_ref": image_ref, "config": cfg.model_dump()})

    # point pipeline output into refs.root
    cfg2 = cfg.model_copy(update={"out_dir": str(refs.root)})

    manifest = run_e2e(
        image_ref=image_ref,
        rig_id=rig_id,
        config=cfg2,
        gemini=gemini,
    )

    # persist manifest explicitly (pipeline already writes it via export_pack; this is belt+suspenders)
    refs.manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"run_id": refs.run_id, "manifest": manifest}
