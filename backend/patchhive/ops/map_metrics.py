"""Map CanonicalRig to RigMetricsPacket."""
from __future__ import annotations

from core.discovery import register_function
from patchhive.schemas import CanonicalRig, RigMetricsPacket


def _score_ratio(numerator: int, denominator: int, weight: float = 1.0) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * weight, 4)


def map_metrics(canonical_rig: CanonicalRig) -> RigMetricsPacket:
    category_counts = canonical_rig.capability_surface
    module_count = len(canonical_rig.modules)
    modulators = category_counts.get("Modulators", 0)
    routers = category_counts.get("Routers / Mix", 0)
    clock = category_counts.get("Clock Domain", 0)
    sources = category_counts.get("Sources", 0)
    shapers = category_counts.get("Shapers", 0)

    modulation_budget = _score_ratio(modulators, module_count, 10.0)
    routing_flex_score = _score_ratio(routers, module_count, 8.0)
    clock_coherence_score = _score_ratio(clock, max(1, sources), 10.0)
    chaos_headroom = _score_ratio(modulators + shapers, module_count, 7.5)
    learning_gradient_index = _score_ratio(
        category_counts.get("Controllers", 0) + routers,
        module_count,
        6.0,
    )
    performance_density_index = _score_ratio(sources + shapers, module_count, 9.0)

    return RigMetricsPacket(
        rig_id=canonical_rig.rig_id,
        module_count=module_count,
        category_counts=category_counts,
        modulation_budget=modulation_budget,
        routing_flex_score=routing_flex_score,
        clock_coherence_score=clock_coherence_score,
        chaos_headroom=chaos_headroom,
        learning_gradient_index=learning_gradient_index,
        performance_density_index=performance_density_index,
    )


register_function(
    name="map_metrics",
    function=map_metrics,
    description="Map CanonicalRig to RigMetricsPacket.",
    input_model="CanonicalRig",
    output_model="RigMetricsPacket",
)
