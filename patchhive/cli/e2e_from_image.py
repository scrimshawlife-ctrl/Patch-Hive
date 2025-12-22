from __future__ import annotations

import json
from pathlib import Path

from patchhive.pipeline.e2e_config import E2EConfig
from patchhive.pipeline.run_e2e import run_e2e
from patchhive.vision.gemini_interface import GeminiVisionClient, VisionRigSpec


class GeminiOverlayClient(GeminiVisionClient):
    """
    Minimal local overlay example:
      - In production: call Gemini API.
      - For dev/tests: load a prepared VisionRigSpec JSON.
    """
    def __init__(self, *, vision_json: str | None = None):
        self.vision_json = vision_json

    def extract_rig(self, image_ref: str, *, rig_id: str) -> VisionRigSpec:
        if not self.vision_json:
            raise RuntimeError("GeminiOverlayClient requires --vision-json in this stub mode.")
        data = json.loads(Path(self.vision_json).read_text(encoding="utf-8"))
        # allow rig_id override
        data["rig_id"] = rig_id
        data["evidence_ref"] = data.get("evidence_ref", f"image:{image_ref}")
        return VisionRigSpec.model_validate(data)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--image-ref", required=True)      # file path or upload id
    ap.add_argument("--rig-id", required=True)

    ap.add_argument("--gallery-root", required=True)
    ap.add_argument("--out-dir", required=True)

    # preset shaping
    ap.add_argument("--preset", default="core")        # starter|core|deep
    ap.add_argument("--rows", type=int, default=1)
    ap.add_argument("--row-hp", type=int, default=104)

    ap.add_argument("--max-total", type=int, default=160)
    ap.add_argument("--max-per-category", type=int, default=70)
    ap.add_argument("--drop-runaway", action="store_true")
    ap.add_argument("--drop-silence", action="store_true")

    # overlay stub (dev)
    ap.add_argument("--vision-json", default=None)

    args = ap.parse_args()

    cfg = E2EConfig(
        gallery_root=args.gallery_root,
        out_dir=args.out_dir,
        preset=args.preset,
        rows=args.rows,
        row_hp=args.row_hp,
        max_total=args.max_total,
        max_per_category=args.max_per_category,
        drop_runaway=bool(args.drop_runaway),
        drop_silence=bool(args.drop_silence),
    )

    gemini = GeminiOverlayClient(vision_json=args.vision_json)

    manifest = run_e2e(
        image_ref=args.image_ref,
        rig_id=args.rig_id,
        config=cfg,
        gemini=gemini,
    )

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
