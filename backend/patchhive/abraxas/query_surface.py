from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from patchhive.schemas import RigMetricsPacket, SuggestedLayout, SymbolicPatchEnvelope


@dataclass(frozen=True)
class RigIndexItem:
    rig_id: str
    metrics: RigMetricsPacket


@dataclass(frozen=True)
class LayoutIndexItem:
    rig_id: str
    layout: SuggestedLayout


@dataclass(frozen=True)
class PatchIndexItem:
    patch_id: str
    envelope: SymbolicPatchEnvelope


def rank_rigs(
    rigs: Iterable[RigIndexItem],
    *,
    key: str,
    descending: bool = True,
    top_k: int = 10,
) -> List[RigIndexItem]:
    """
    Rank rigs by a metric field on RigMetricsPacket.
    Deterministic tie-break: rig_id.
    """
    items = list(rigs)

    def metric_value(item: RigIndexItem) -> float:
        m = item.metrics
        if not hasattr(m, key):
            raise ValueError(f"Unknown rig metric key: {key}")
        return float(getattr(m, key))

    items.sort(
        key=lambda it: (-metric_value(it) if descending else metric_value(it), it.rig_id)
    )
    return items[: max(0, top_k)]


def rank_layouts(
    layouts: Iterable[LayoutIndexItem],
    *,
    key: str,
    descending: bool = True,
    top_k: int = 10,
) -> List[LayoutIndexItem]:
    """
    Rank layouts by either:
      - total_score
      - score_breakdown.<field>
    Deterministic tie-break: (rig_id, layout_type).
    """
    items = list(layouts)

    def value(it: LayoutIndexItem) -> float:
        layout = it.layout
        if key == "total_score":
            return float(layout.total_score)
        if key.startswith("score_breakdown."):
            field = key.split(".", 1)[1]
            breakdown = layout.score_breakdown
            if not hasattr(breakdown, field):
                raise ValueError(f"Unknown layout breakdown key: {field}")
            return float(getattr(breakdown, field))
        raise ValueError(f"Unsupported layout key: {key}")

    items.sort(
        key=lambda it: (
            -value(it) if descending else value(it),
            it.rig_id,
            it.layout.layout_type.value,
        )
    )
    return items[: max(0, top_k)]


def filter_patches(
    patches: Iterable[PatchIndexItem],
    *,
    min_closure_strength: Optional[float] = None,
    max_chaos_mean: Optional[float] = None,
    min_performer_agency: Optional[float] = None,
    top_k: int = 10,
) -> List[PatchIndexItem]:
    """
    Filter patches by envelope constraints, then rank deterministically by:
      closure_strength desc, performer agency desc, chaos mean asc, patch_id.
    """
    filtered: List[PatchIndexItem] = []
    for item in patches:
        env = item.envelope
        chaos_mean = (
            sum(env.chaos_modulation_curve) / max(1, len(env.chaos_modulation_curve))
            if env.chaos_modulation_curve
            else 0.0
        )
        performer = float(env.agency_distribution.get("performer", 0.0))

        if min_closure_strength is not None and env.closure_strength < min_closure_strength:
            continue
        if max_chaos_mean is not None and chaos_mean > max_chaos_mean:
            continue
        if min_performer_agency is not None and performer < min_performer_agency:
            continue

        filtered.append(item)

    def chaos_mean(item: PatchIndexItem) -> float:
        curve = item.envelope.chaos_modulation_curve
        return (sum(curve) / max(1, len(curve))) if curve else 0.0

    filtered.sort(
        key=lambda item: (
            -item.envelope.closure_strength,
            -float(item.envelope.agency_distribution.get("performer", 0.0)),
            chaos_mean(item),
            item.patch_id,
        )
    )
    return filtered[: max(0, top_k)]
