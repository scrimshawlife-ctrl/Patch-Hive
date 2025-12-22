from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.derive_symbolic_envelope import derive_symbolic_envelope
from patchhive.ops.generate_patch import generate_patch
from patchhive.ops.map_metrics import map_metrics
from patchhive.ops.suggest_layouts import CaseSpec, suggest_layouts
from patchhive.ops.validate_patch import validate_patch
from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    PatchHiveBundle,
    PatchIntent,
    Provenance,
    ProvenanceType,
    RigSpec,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _bundle_meta(rig_id: str, seed: int) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=f"rig:{rig_id}:seed:{seed}",
                method="pipeline.run.v1",
            )
        ],
        confidence=0.9,
        status=FieldStatus.inferred,
    )


def run_pipeline(
    *,
    rig: RigSpec,
    gallery_root: str,
    intent: PatchIntent,
    seed: int,
    case: CaseSpec = CaseSpec(),
    image_id: Optional[str] = None,
) -> PatchHiveBundle:
    """
    No side effects beyond reading the gallery store.
    (Phase 8 confirmation is separate by design.)
    """
    gallery = ModuleGalleryStore(gallery_root)

    canon = build_canonical_rig(rig, gallery_store=gallery)
    metrics = map_metrics(canon)
    layouts = suggest_layouts(canon, metrics, case=case)

    out = generate_patch(canon, intent=intent, seed=seed)
    patch = out["patch"]
    plan = out["plan"]
    validation = out["validation"]
    variations = out["variations"]

    validation = validate_patch(patch, plan)
    envelope = derive_symbolic_envelope(patch, plan)

    return PatchHiveBundle(
        image_id=image_id,
        rig_id=canon.rig_id,
        canonical_rig=canon,
        metrics=metrics,
        layouts=layouts,
        patch=patch,
        plan=plan,
        validation=validation,
        envelope=envelope,
        variations=variations,
        meta=_bundle_meta(canon.rig_id, seed),
    )
