from __future__ import annotations

import json
from pathlib import Path

from patchhive.pipeline.e2e_config import E2EConfig
from patchhive.pipeline.run_e2e import run_e2e
from patchhive.vision.gemini_interface import GeminiVisionClient, VisionRigSpec


class StubGemini(GeminiVisionClient):
    def __init__(self, vision: VisionRigSpec):
        self._vision = vision

    def extract_rig(self, image_ref: str, *, rig_id: str) -> VisionRigSpec:
        v = self._vision.model_copy(update={"rig_id": rig_id, "evidence_ref": f"image:{image_ref}"})
        return v


def test_e2e_pipeline_writes_bundle(tmp_path: Path):
    # minimal vision spec: one module hit
    vision = VisionRigSpec.model_validate({
        "rig_id": "rig.stub",
        "evidence_ref": "vision:stub",
        "modules": [
            {"module_name": "Voltage Lab 2", "manufacturer": "Pittsburgh Modular", "hp": 104,
             "jack_labels": ["CLK OUT", "GATE IN", "AUDIO OUT", "AUDIO IN"]}
        ],
    })

    cfg = E2EConfig(
        gallery_root=str(tmp_path / "gallery"),
        out_dir=str(tmp_path / "out"),
        preset="starter",
        rows=1,
        row_hp=104,
        max_total=10,
        max_per_category=10,
    )

    gemini = StubGemini(vision)

    manifest = run_e2e(
        image_ref="file:rig.png",
        rig_id="rig.test",
        config=cfg,
        gemini=gemini,
    )

    out = Path(cfg.out_dir)
    assert (out / "rigspec.json").exists()
    assert (out / "json" / "library.json").exists()
    assert (out / "manifest.json").exists()
    assert (out / "summary.json").exists()
    assert (out / "pdf" / "patchbook.pdf").exists()
    assert (out / "svgs").exists()
    assert any(p.suffix == ".svg" for p in (out / "svgs").iterdir())
    assert "hashes" in manifest and manifest["hashes"]
