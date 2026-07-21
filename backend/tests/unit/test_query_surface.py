"""Canon query surface rank/filter helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from canon.contracts import (
    EpistemicStatus,
    LayoutPlacement,
    RigMetricsPacket,
    SuggestedLayout,
)
from canon.query_surface import (
    LayoutIndexItem,
    PatchEnvelopeView,
    PatchIndexItem,
    RigIndexItem,
    filter_patches,
    rank_layouts,
    rank_rigs,
)

NOW = datetime(2025, 12, 21, tzinfo=timezone.utc)


def _metrics(*, artifact_id: str, score: float, entity: str = "rig-rev-a") -> RigMetricsPacket:
    return RigMetricsPacket(
        artifact_id=artifact_id,
        entity_id=entity,
        generator_version="canon-metrics.1.0.0",
        generation_seed=1,
        source_run_id="gen-run-1",
        source_rig_revision_id=entity,
        created_at=NOW,
        module_count=2,
        total_hp=20,
        routing_flex_score=score,
    ).seal()


def _layout(*, layout_id: str, score: float, rig_entity: str = "rig-rev-a") -> SuggestedLayout:
    return SuggestedLayout(
        artifact_id=layout_id,
        entity_id=rig_entity,
        generator_version="canon-layout.1.0.0",
        generation_seed=1,
        source_run_id="gen-run-1",
        source_rig_revision_id=rig_entity,
        created_at=NOW,
        layout_id=layout_id,
        label=layout_id,
        placements=(LayoutPlacement(instance_id="osc", row=0, start_hp=0),),
        score=score,
        status=EpistemicStatus.confirmed,
    ).seal()


def test_rank_and_filter_end_to_end() -> None:
    rigs = [
        RigIndexItem(rig_id="rig-low", metrics=_metrics(artifact_id="m-low", score=1.0)),
        RigIndexItem(rig_id="rig-high", metrics=_metrics(artifact_id="m-high", score=3.5)),
    ]
    ranked = rank_rigs(rigs, key="routing_flex_score", top_k=5)
    assert ranked[0].rig_id == "rig-high"

    layouts = [
        LayoutIndexItem(rig_id="rig-high", layout=_layout(layout_id="lay-a", score=0.9)),
        LayoutIndexItem(rig_id="rig-high", layout=_layout(layout_id="lay-b", score=0.5)),
        LayoutIndexItem(rig_id="rig-high", layout=_layout(layout_id="lay-c", score=0.7)),
    ]
    lrank = rank_layouts(layouts, key="score", top_k=3)
    assert len(lrank) == 3
    assert lrank[0].layout.layout_id == "lay-a"

    pitems = [
        PatchIndexItem(
            patch_id="patch-weak",
            envelope=PatchEnvelopeView(
                patch_id="patch-weak",
                closure_strength=0.1,
                chaos_modulation_curve=(0.9,),
                agency_distribution={"performer": 0.05},
            ),
        ),
        PatchIndexItem(
            patch_id="patch-strong",
            envelope=PatchEnvelopeView(
                patch_id="patch-strong",
                closure_strength=0.8,
                chaos_modulation_curve=(0.2, 0.3),
                agency_distribution={"performer": 0.7},
            ),
        ),
    ]
    picked = filter_patches(
        pitems,
        min_closure_strength=0.2,
        max_chaos_mean=1.0,
        min_performer_agency=0.1,
        top_k=1,
    )
    assert picked and picked[0].patch_id == "patch-strong"
