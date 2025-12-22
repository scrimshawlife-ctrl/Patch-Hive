from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Set

from patchhive.schemas import (
    CapabilityCategory,
    CanonicalRig,
    FieldMeta,
    FieldStatus,
    Provenance,
    ProvenanceType,
    RigMetricsPacket,
    SignalKind,
)


# ----------------------------
# Category mapping (v1, deterministic)
# ----------------------------

# Minimal kind->category rules. We intentionally keep this conservative in v1.
KIND_TO_CATEGORY: Dict[SignalKind, CapabilityCategory] = {
    SignalKind.audio: CapabilityCategory.sources,
    SignalKind.pitch_cv: CapabilityCategory.controllers,
    SignalKind.gate: CapabilityCategory.controllers,
    SignalKind.trigger: CapabilityCategory.controllers,
    SignalKind.clock: CapabilityCategory.clock_domain,
    SignalKind.envelope: CapabilityCategory.controllers,
    SignalKind.lfo: CapabilityCategory.modulators,
    SignalKind.random: CapabilityCategory.modulators,
    SignalKind.midi: CapabilityCategory.io_external,
    SignalKind.cv: CapabilityCategory.modulators,
    SignalKind.cv_or_audio: CapabilityCategory.sources,
    SignalKind.unknown: CapabilityCategory.normals_internal,
}

# Tag hints on modules/modes to improve category inference without hardcoding vendors.
TAG_HINTS: Dict[str, CapabilityCategory] = {
    "oscillator": CapabilityCategory.sources,
    "noise": CapabilityCategory.sources,
    "source": CapabilityCategory.sources,
    "filter": CapabilityCategory.shapers,
    "waveshaper": CapabilityCategory.shapers,
    "lpg": CapabilityCategory.shapers,
    "shaper": CapabilityCategory.shapers,
    "sequencer": CapabilityCategory.controllers,
    "envelope": CapabilityCategory.controllers,
    "controller": CapabilityCategory.controllers,
    "lfo": CapabilityCategory.modulators,
    "random": CapabilityCategory.modulators,
    "modulator": CapabilityCategory.modulators,
    "vca": CapabilityCategory.routers_mix,
    "mixer": CapabilityCategory.routers_mix,
    "attenuator": CapabilityCategory.routers_mix,
    "attenuverter": CapabilityCategory.routers_mix,
    "router": CapabilityCategory.routers_mix,
    "clock": CapabilityCategory.clock_domain,
    "divider": CapabilityCategory.clock_domain,
    "multiplier": CapabilityCategory.clock_domain,
    "delay": CapabilityCategory.fx_space,
    "reverb": CapabilityCategory.fx_space,
    "fx": CapabilityCategory.fx_space,
    "output": CapabilityCategory.io_external,
    "input": CapabilityCategory.io_external,
    "io": CapabilityCategory.io_external,
    "semi-normalled": CapabilityCategory.normals_internal,
    "normalled": CapabilityCategory.normals_internal,
}


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta_derived(rig_id: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=f"rig:{rig_id}",
                method="map_metrics.v1",
            )
        ],
        confidence=0.9,
        status=FieldStatus.inferred,
    )


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def _tags_to_categories(tags: List[str]) -> Set[CapabilityCategory]:
    cats: Set[CapabilityCategory] = set()
    for t in tags:
        key = t.strip().lower()
        if key in TAG_HINTS:
            cats.add(TAG_HINTS[key])
    return cats


def _module_categories(canon_module) -> Set[CapabilityCategory]:
    """
    Determine module categories using:
    1) tag hints (module tags + mode tags)
    2) jack signal kinds (fallback)
    """
    cats = set()

    cats |= _tags_to_categories(canon_module.tags)

    # include mode tags as hints
    for m in canon_module.modes:
        cats |= _tags_to_categories(m.tags)

    if cats:
        return cats

    # fallback: jack-based inference
    for j in canon_module.jacks:
        cats.add(KIND_TO_CATEGORY.get(j.signal.kind, CapabilityCategory.normals_internal))

    return cats or {CapabilityCategory.normals_internal}


def map_metrics(canon: CanonicalRig) -> RigMetricsPacket:
    """
    Deterministic RigMetricsPacket v1.
    Conservative heuristics; tuned later via explicit versioning.

    Outputs:
    - category_counts
    - modulation_budget
    - routing_flex_score
    - clock_coherence_score
    - chaos_headroom
    - learning_gradient_index
    - performance_density_index
    """
    # Stable ordering by instance_id already enforced upstream; still treat as set-like here.
    module_count = len(canon.modules)

    # Category counts: count module membership per category (modules can contribute to multiple cats).
    cat_counter: Counter = Counter()
    for mod in canon.modules:
        for cat in _module_categories(mod):
            cat_counter[cat] += 1

    category_counts: Dict[CapabilityCategory, int] = dict(cat_counter)

    # Convenience getters
    def c(cat: CapabilityCategory) -> int:
        return int(category_counts.get(cat, 0))

    sources = c(CapabilityCategory.sources)
    shapers = c(CapabilityCategory.shapers)
    controllers = c(CapabilityCategory.controllers)
    modulators = c(CapabilityCategory.modulators)
    routers = c(CapabilityCategory.routers_mix)
    clocks = c(CapabilityCategory.clock_domain)
    fx = c(CapabilityCategory.fx_space)
    io = c(CapabilityCategory.io_external)
    normals = c(CapabilityCategory.normals_internal)

    # ----------------------------
    # Scores (v1 formulas)
    # ----------------------------

    # Modulation budget: modulators + controllers, scaled by routing capacity (routers/mix).
    # If you can't route modulation, budget is theoretical.
    modulation_budget = float(modulators + 0.6 * controllers) * (1.0 + 0.25 * routers)

    # Routing flexibility: routers/mix + normals/internal busses + total diversity.
    diversity = len([x for x in [sources, shapers, controllers, modulators, routers, clocks, fx, io] if x > 0])
    routing_flex_score = float(routers) * 1.2 + float(normals) * 0.8 + float(diversity) * 0.5

    # Clock coherence: more clock tools help, but too few controllers hurts musical coherence.
    # Normalize to roughly 0..1 with conservative clamp.
    raw_clock = (clocks * 0.35) + (controllers * 0.15) - (max(0, modulators - controllers) * 0.05)
    clock_coherence_score = _clamp01(raw_clock)

    # Chaos headroom: ability to introduce randomness safely
    # = modulators (esp random/lfo) balanced by shapers/routers (containment).
    raw_chaos = (modulators * 0.20) + (shapers * 0.10) + (routers * 0.15) - (max(0, modulators - routers - 1) * 0.07)
    chaos_headroom = _clamp01(raw_chaos)

    # Learning gradient: clear pedagogy tends to correlate with balanced counts + clock + routing.
    # Penalize rigs that are all sources/modulators with no routing/clock.
    base = (diversity * 0.10) + (clocks * 0.20) + (routers * 0.20) + (controllers * 0.10)
    penalty = 0.15 if (routers == 0 or clocks == 0) else 0.0
    learning_gradient_index = _clamp01(base - penalty)

    # Performance density: how much immediate performability exists per module.
    # Controllers + routers + fx help; normalize by module_count.
    denom = max(1, module_count)
    perf_raw = (controllers * 0.35 + routers * 0.30 + fx * 0.20 + io * 0.10) / denom
    performance_density_index = _clamp01(perf_raw)

    return RigMetricsPacket(
        rig_id=canon.rig_id,
        module_count=module_count,
        category_counts=category_counts,
        modulation_budget=float(modulation_budget),
        routing_flex_score=float(routing_flex_score),
        clock_coherence_score=float(clock_coherence_score),
        chaos_headroom=float(chaos_headroom),
        learning_gradient_index=float(learning_gradient_index),
        performance_density_index=float(performance_density_index),
        meta=_meta_derived(canon.rig_id),
    )
