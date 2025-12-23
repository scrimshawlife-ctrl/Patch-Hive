from __future__ import annotations

from pathlib import Path

from patchhive.abraxas.query_surface import (
    LayoutIndexItem,
    PatchIndexItem,
    RigIndexItem,
    filter_patches,
    rank_layouts,
    rank_rigs,
)
from patchhive.fixtures.basic_voice_fixture import gallery_voice_entry, rigspec_voice_min
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.derive_symbolic_envelope import derive_symbolic_envelope
from patchhive.ops.generate_patch import generate_patch
from patchhive.ops.map_metrics import map_metrics
from patchhive.ops.suggest_layouts import CaseSpec, suggest_layouts
from patchhive.schemas import FieldMeta, FieldStatus, PatchIntent, Provenance, ProvenanceType


def _intent(archetype: str) -> PatchIntent:
    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=__import__("datetime").datetime(
                    2025, 12, 21, tzinfo=__import__("datetime").timezone.utc
                ),
                evidence_ref="test",
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )
    return PatchIntent(archetype=archetype, energy="medium", focus="learnability", meta=meta)


def test_rank_and_filter_end_to_end(tmp_path: Path) -> None:
    store = ModuleGalleryStore(tmp_path)
    store.append_revision(gallery_voice_entry())

    rig = rigspec_voice_min()
    canon = build_canonical_rig(rig, gallery_store=store)
    metrics = map_metrics(canon)
    layouts = suggest_layouts(canon, metrics, case=CaseSpec(rows=1, row_hp=104))

    out = generate_patch(canon, intent=_intent("generative_mod"), seed=42)
    env = derive_symbolic_envelope(out["patch"], out["plan"])

    rigs = [RigIndexItem(rig_id=canon.rig_id, metrics=metrics)]
    ranked = rank_rigs(rigs, key="routing_flex_score", top_k=5)
    assert ranked[0].rig_id == canon.rig_id

    litems = [LayoutIndexItem(rig_id=canon.rig_id, layout=l) for l in layouts]
    lrank = rank_layouts(litems, key="score_breakdown.learning_gradient", top_k=3)
    assert len(lrank) == 3

    pitems = [PatchIndexItem(patch_id=env.patch_id, envelope=env)]
    picked = filter_patches(
        pitems,
        min_closure_strength=0.2,
        max_chaos_mean=1.0,
        min_performer_agency=0.1,
        top_k=1,
    )
    assert picked and picked[0].patch_id == env.patch_id
