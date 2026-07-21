"""Deterministic rank/filter helpers for Abraxas-facing indexes (CANON_MVP).

Historical implementation: ``patchhive.abraxas.query_surface``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from canon.contracts import RigMetricsPacket, SuggestedLayout


@dataclass(frozen=True)
class RigIndexItem:
    rig_id: str
    metrics: RigMetricsPacket


@dataclass(frozen=True)
class LayoutIndexItem:
    rig_id: str
    layout: SuggestedLayout


@dataclass(frozen=True)
class PatchEnvelopeView:
    """Lightweight envelope for filter/rank without historical SymbolicPatchEnvelope."""

    patch_id: str
    closure_strength: float
    chaos_modulation_curve: tuple[float, ...] = ()
    agency_distribution: dict[str, float] | None = None

    def __post_init__(self) -> None:
        if self.agency_distribution is None:
            object.__setattr__(self, "agency_distribution", {})


@dataclass(frozen=True)
class PatchIndexItem:
    patch_id: str
    envelope: PatchEnvelopeView


def rank_rigs(
    rigs: Iterable[RigIndexItem],
    *,
    key: str,
    descending: bool = True,
    top_k: int = 10,
) -> list[RigIndexItem]:
    items = list(rigs)

    def metric_value(item: RigIndexItem) -> float:
        if not hasattr(item.metrics, key):
            raise ValueError(f"Unknown rig metric key: {key}")
        return float(getattr(item.metrics, key))

    items.sort(key=lambda it: (-metric_value(it) if descending else metric_value(it), it.rig_id))
    return items[: max(0, top_k)]


def rank_layouts(
    layouts: Iterable[LayoutIndexItem],
    *,
    key: str = "score",
    descending: bool = True,
    top_k: int = 10,
) -> list[LayoutIndexItem]:
    items = list(layouts)

    def value(it: LayoutIndexItem) -> float:
        if key in {"score", "total_score"}:
            return float(it.layout.score)
        raise ValueError(f"Unsupported layout key: {key}")

    items.sort(
        key=lambda it: (
            -value(it) if descending else value(it),
            it.rig_id,
            it.layout.layout_id,
        )
    )
    return items[: max(0, top_k)]


def filter_patches(
    patches: Iterable[PatchIndexItem],
    *,
    min_closure_strength: float | None = None,
    max_chaos_mean: float | None = None,
    min_performer_agency: float | None = None,
    top_k: int = 10,
) -> list[PatchIndexItem]:
    filtered: list[PatchIndexItem] = []
    for item in patches:
        env = item.envelope
        curve = env.chaos_modulation_curve
        chaos_mean = (sum(curve) / max(1, len(curve))) if curve else 0.0
        agency = env.agency_distribution or {}
        performer = float(agency.get("performer", 0.0))

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
            -float((item.envelope.agency_distribution or {}).get("performer", 0.0)),
            chaos_mean(item),
            item.patch_id,
        )
    )
    return filtered[: max(0, top_k)]
