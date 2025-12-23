from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from patchhive.ops.suggest_layouts import CaseSpec
from patchhive.pipeline.run import run_pipeline
from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    PatchIntent,
    Provenance,
    ProvenanceType,
    RigSpec,
)


def _intent_meta() -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=datetime.now(timezone.utc),
                evidence_ref="cli:intent",
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--rigspec", required=True, help="Path to RigSpec JSON")
    ap.add_argument("--gallery-root", required=True)
    ap.add_argument("--out", required=True, help="Output path for bundle JSON")
    ap.add_argument("--archetype", default="generative_mod")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--rows", type=int, default=1)
    ap.add_argument("--row-hp", type=int, default=104)
    ap.add_argument("--image-id", default=None)
    args = ap.parse_args()

    rig = RigSpec.model_validate(json.loads(Path(args.rigspec).read_text(encoding="utf-8")))
    intent = PatchIntent(
        archetype=args.archetype,
        energy="medium",
        focus="learnability",
        meta=_intent_meta(),
    )

    bundle = run_pipeline(
        rig=rig,
        gallery_root=args.gallery_root,
        intent=intent,
        seed=args.seed,
        case=CaseSpec(rows=args.rows, row_hp=args.row_hp),
        image_id=args.image_id,
    )

    Path(args.out).write_text(bundle.to_canonical_json(), encoding="utf-8")
    print(f"Wrote bundle: {args.out}")


if __name__ == "__main__":
    main()
