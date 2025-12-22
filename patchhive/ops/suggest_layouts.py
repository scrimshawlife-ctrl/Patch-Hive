from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from patchhive.schemas import (
    CapabilityCategory,
    CanonicalRig,
    FieldMeta,
    FieldStatus,
    LayoutPlacement,
    LayoutScoreBreakdown,
    LayoutType,
    Provenance,
    ProvenanceType,
    RigMetricsPacket,
    SuggestedLayout,
)


@dataclass(frozen=True)
class CaseSpec:
    rows: int = 1
    row_hp: int = 104


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta_derived(rig_id: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=f"rig:{rig_id}",
                method="suggest_layouts.v1",
            )
        ],
        confidence=0.85,
        status=FieldStatus.inferred,
    )


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def _module_primary_category(mod, metrics: RigMetricsPacket) -> CapabilityCategory:
    """
    Deterministic, conservative category assignment for layout purposes.
    Uses module tags/mode tags when available, otherwise falls back to rig-wide counts.
    (True category inference is in map_metrics; here we need a stable heuristic.)
    """
    tags = " ".join([t.lower() for t in (mod.tags or [])])
    mode_tags = " ".join([(" ".join(m.tags)).lower() for m in (mod.modes or [])])

    blob = f"{tags} {mode_tags}"

    # Order matters: earlier = higher priority.
    rules: List[Tuple[str, CapabilityCategory]] = [
        ("clock", CapabilityCategory.clock_domain),
        ("sequencer", CapabilityCategory.controllers),
        ("controller", CapabilityCategory.controllers),
        ("envelope", CapabilityCategory.controllers),
        ("lfo", CapabilityCategory.modulators),
        ("random", CapabilityCategory.modulators),
        ("modulator", CapabilityCategory.modulators),
        ("vca", CapabilityCategory.routers_mix),
        ("mixer", CapabilityCategory.routers_mix),
        ("attenuverter", CapabilityCategory.routers_mix),
        ("attenuator", CapabilityCategory.routers_mix),
        ("filter", CapabilityCategory.shapers),
        ("waveshaper", CapabilityCategory.shapers),
        ("lpg", CapabilityCategory.shapers),
        ("delay", CapabilityCategory.fx_space),
        ("reverb", CapabilityCategory.fx_space),
        ("fx", CapabilityCategory.fx_space),
        ("output", CapabilityCategory.io_external),
        ("input", CapabilityCategory.io_external),
        ("io", CapabilityCategory.io_external),
        ("oscillator", CapabilityCategory.sources),
        ("noise", CapabilityCategory.sources),
        ("source", CapabilityCategory.sources),
        ("semi-normalled", CapabilityCategory.normals_internal),
        ("normalled", CapabilityCategory.normals_internal),
    ]
    for key, cat in rules:
        if key in blob:
            return cat

    # Fallback: pick the most common categories in the rig (stable tie-break order)
    # so unknown modules don’t random-walk.
    preferred = [
        CapabilityCategory.controllers,
        CapabilityCategory.clock_domain,
        CapabilityCategory.routers_mix,
        CapabilityCategory.sources,
        CapabilityCategory.shapers,
        CapabilityCategory.modulators,
        CapabilityCategory.fx_space,
        CapabilityCategory.io_external,
        CapabilityCategory.normals_internal,
    ]
    counts = metrics.category_counts
    best = max(preferred, key=lambda c: (counts.get(c, 0), -preferred.index(c)))
    return best


def _touch_weight(cat: CapabilityCategory) -> float:
    # Performance ergonomics: controllers/clocks/routers most touched
    return {
        CapabilityCategory.controllers: 1.0,
        CapabilityCategory.clock_domain: 0.9,
        CapabilityCategory.routers_mix: 0.85,
        CapabilityCategory.modulators: 0.6,
        CapabilityCategory.sources: 0.55,
        CapabilityCategory.shapers: 0.55,
        CapabilityCategory.fx_space: 0.5,
        CapabilityCategory.io_external: 0.35,
        CapabilityCategory.normals_internal: 0.25,
    }[cat]


def _pack_rows(mods: List[Tuple[str, int]], case: CaseSpec) -> Dict[str, Tuple[int, int]]:
    """
    Deterministic first-fit row packing.
    Returns instance_id -> (row, x_hp).
    Raises if overflow.
    """
    remaining = [case.row_hp for _ in range(case.rows)]
    cursor = [0 for _ in range(case.rows)]
    placement: Dict[str, Tuple[int, int]] = {}

    for instance_id, hp in mods:
        placed = False
        for r in range(case.rows):
            if remaining[r] >= hp:
                placement[instance_id] = (r, cursor[r])
                cursor[r] += hp
                remaining[r] -= hp
                placed = True
                break
        if not placed:
            raise ValueError(
                f"Case overflow: cannot place {instance_id} ({hp}hp) into {case.rows}x{case.row_hp}hp"
            )

    return placement


def _score_layout(
    canon: CanonicalRig,
    metrics: RigMetricsPacket,
    placement: Dict[str, Tuple[int, int]],
    case: CaseSpec,
) -> LayoutScoreBreakdown:
    """
    Deterministic heuristic scoring.
    - reach_cost: weighted distance of touch-heavy modules from center
    - cable_cross_cost: proxy using desired adjacency distances between category pairs
    - learning_gradient: monotonic left->right category ordering score
    - utility_proximity: routers near controllers/sources/shapers/modulators
    - patch_template_coverage: proxy using rig diversity + adjacency quality
    """
    center_x = case.row_hp / 2.0

    # Category per module
    cats: Dict[str, CapabilityCategory] = {}
    for m in canon.modules:
        cats[m.instance_id] = _module_primary_category(m, metrics)

    # Reach cost
    reach = 0.0
    for m in canon.modules:
        r, x = placement[m.instance_id]
        # approximate module "center"
        x_center = x + (m.hp / 2.0)
        reach += abs(x_center - center_x) * _touch_weight(cats[m.instance_id])

    # Normalize reach cost to 0..1 where lower is better (we keep raw cost but scale)
    reach_cost = max(0.0, reach / (case.row_hp * max(1, len(canon.modules))))

    # Cable cross proxy: encourage short distances between common pairs
    # (controller->source, source->shaper, shaper->router, router->fx, controller->modulator)
    pairs = [
        (CapabilityCategory.controllers, CapabilityCategory.sources, 1.0),
        (CapabilityCategory.sources, CapabilityCategory.shapers, 0.9),
        (CapabilityCategory.shapers, CapabilityCategory.routers_mix, 1.0),
        (CapabilityCategory.routers_mix, CapabilityCategory.fx_space, 0.7),
        (CapabilityCategory.controllers, CapabilityCategory.modulators, 0.8),
    ]

    def avg_distance(cat_a: CapabilityCategory, cat_b: CapabilityCategory) -> float:
        a = [m for m in canon.modules if cats[m.instance_id] == cat_a]
        b = [m for m in canon.modules if cats[m.instance_id] == cat_b]
        if not a or not b:
            return 0.0
        # average distance between centers (cheap O(n^2) is fine for v1 sizes)
        dsum, cnt = 0.0, 0
        for ma in a:
            ra, xa = placement[ma.instance_id]
            ca = xa + ma.hp / 2.0
            for mb in b:
                rb, xb = placement[mb.instance_id]
                cb = xb + mb.hp / 2.0
                # add small penalty for different rows
                row_pen = 0.15 * abs(ra - rb)
                dsum += abs(ca - cb) + row_pen * case.row_hp
                cnt += 1
        return dsum / cnt

    cable = 0.0
    for a, b, w in pairs:
        cable += avg_distance(a, b) * w

    cable_cross_cost = max(0.0, cable / (case.row_hp * max(1, len(pairs))))

    # Learning gradient: measure how well categories are grouped left->right in canonical “teaching flow”
    flow = [
        CapabilityCategory.clock_domain,
        CapabilityCategory.controllers,
        CapabilityCategory.sources,
        CapabilityCategory.shapers,
        CapabilityCategory.routers_mix,
        CapabilityCategory.fx_space,
        CapabilityCategory.io_external,
        CapabilityCategory.normals_internal,
    ]
    # compute average x position per category present
    cat_pos: Dict[CapabilityCategory, float] = {}
    for cat in flow:
        xs = []
        for m in canon.modules:
            if cats[m.instance_id] == cat:
                r, x = placement[m.instance_id]
                xs.append(x + m.hp / 2.0)
        if xs:
            cat_pos[cat] = sum(xs) / len(xs)

    # score monotonicity: how often positions follow flow order
    present = [cat for cat in flow if cat in cat_pos]
    if len(present) <= 1:
        learning_gradient = 0.5
    else:
        inversions = 0
        total = 0
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                total += 1
                if cat_pos[present[i]] > cat_pos[present[j]]:
                    inversions += 1
        learning_gradient = _clamp01(1.0 - (inversions / max(1, total)))

    # Utility proximity: routers close to (controllers, sources, shapers, modulators)
    prox_targets = [
        CapabilityCategory.controllers,
        CapabilityCategory.sources,
        CapabilityCategory.shapers,
        CapabilityCategory.modulators,
    ]
    prox = 0.0
    for t in prox_targets:
        prox += avg_distance(CapabilityCategory.routers_mix, t)
    utility_proximity = _clamp01(1.0 - (prox / (case.row_hp * max(1, len(prox_targets)))))

    # Patch template coverage: diversity + good adjacency (inverse of cable cost) + clock presence
    diversity = len([k for k, v in metrics.category_counts.items() if v > 0])
    diversity_score = _clamp01(diversity / 9.0)
    patch_template_coverage = _clamp01(
        0.45 * diversity_score
        + 0.35 * (1.0 - _clamp01(cable_cross_cost))
        + 0.20 * (_clamp01(metrics.clock_coherence_score))
    )

    return LayoutScoreBreakdown(
        reach_cost=float(reach_cost),
        cable_cross_cost=float(cable_cross_cost),
        learning_gradient=float(learning_gradient),
        utility_proximity=float(utility_proximity),
        patch_template_coverage=float(patch_template_coverage),
    )


def _total_score(b: LayoutScoreBreakdown) -> float:
    """
    Higher is better. We invert costs and weight clarity/utility.
    """
    return float(
        0.30 * (1.0 - _clamp01(b.reach_cost))
        + 0.25 * (1.0 - _clamp01(b.cable_cross_cost))
        + 0.20 * _clamp01(b.learning_gradient)
        + 0.15 * _clamp01(b.utility_proximity)
        + 0.10 * _clamp01(b.patch_template_coverage)
    )


def _layout_order_beginner(canon: CanonicalRig, metrics: RigMetricsPacket) -> List[str]:
    """
    Teaching flow left->right.
    """
    flow = [
        CapabilityCategory.clock_domain,
        CapabilityCategory.controllers,
        CapabilityCategory.sources,
        CapabilityCategory.shapers,
        CapabilityCategory.routers_mix,
        CapabilityCategory.fx_space,
        CapabilityCategory.io_external,
        CapabilityCategory.normals_internal,
        CapabilityCategory.modulators,  # modulators placed near controllers/sources if possible; beginner puts them later
    ]
    cats = {m.instance_id: _module_primary_category(m, metrics) for m in canon.modules}
    # stable: within category, sort by instance_id
    out: List[str] = []
    for cat in flow:
        out.extend(sorted([m.instance_id for m in canon.modules if cats[m.instance_id] == cat]))
    # any leftovers (shouldn't happen) appended deterministically
    leftovers = [m.instance_id for m in canon.modules if m.instance_id not in out]
    out.extend(sorted(leftovers))
    return out


def _layout_order_performance(canon: CanonicalRig, metrics: RigMetricsPacket) -> List[str]:
    """
    Center controllers/clocks/routers by row-packing ordering:
    We approximate “center priority” by ordering:
      controllers, clocks, routers, modulators, sources, shapers, fx, io, normals
    Then scoring will reward their proximity to the center.
    """
    priority = [
        CapabilityCategory.controllers,
        CapabilityCategory.clock_domain,
        CapabilityCategory.routers_mix,
        CapabilityCategory.modulators,
        CapabilityCategory.sources,
        CapabilityCategory.shapers,
        CapabilityCategory.fx_space,
        CapabilityCategory.io_external,
        CapabilityCategory.normals_internal,
    ]
    cats = {m.instance_id: _module_primary_category(m, metrics) for m in canon.modules}
    out: List[str] = []
    for cat in priority:
        out.extend(sorted([m.instance_id for m in canon.modules if cats[m.instance_id] == cat]))
    leftovers = [m.instance_id for m in canon.modules if m.instance_id not in out]
    out.extend(sorted(leftovers))
    return out


def _layout_order_experimental(canon: CanonicalRig, metrics: RigMetricsPacket) -> List[str]:
    """
    Interleave categories to reduce long runs:
      (clock/controllers) -> modulators -> sources -> shapers -> routers -> fx -> io -> normals
    This tends to create short “triangles” for generative patches.
    """
    cats = {m.instance_id: _module_primary_category(m, metrics) for m in canon.modules}

    buckets: Dict[CapabilityCategory, List[str]] = {}
    for m in canon.modules:
        buckets.setdefault(cats[m.instance_id], []).append(m.instance_id)
    for k in buckets:
        buckets[k] = sorted(buckets[k])

    pattern = [
        CapabilityCategory.clock_domain,
        CapabilityCategory.controllers,
        CapabilityCategory.modulators,
        CapabilityCategory.sources,
        CapabilityCategory.shapers,
        CapabilityCategory.routers_mix,
        CapabilityCategory.fx_space,
        CapabilityCategory.io_external,
        CapabilityCategory.normals_internal,
    ]

    out: List[str] = []
    # round-robin pull
    remaining = True
    while remaining:
        remaining = False
        for cat in pattern:
            if buckets.get(cat):
                out.append(buckets[cat].pop(0))
                remaining = True

    leftovers = [m.instance_id for m in canon.modules if m.instance_id not in out]
    out.extend(sorted(leftovers))
    return out


def suggest_layouts(
    canon: CanonicalRig,
    metrics: RigMetricsPacket,
    *,
    case: CaseSpec = CaseSpec(),
) -> List[SuggestedLayout]:
    """
    Produce exactly three deterministic layouts:
      Beginner, Performance, Experimental
    """
    # prepare (instance_id, hp)
    hp_map = {m.instance_id: m.hp for m in canon.modules}

    def build(layout_type: LayoutType, order: List[str], rationale: str) -> SuggestedLayout:
        mods = [(iid, hp_map[iid]) for iid in order]
        placement = _pack_rows(mods, case)
        breakdown = _score_layout(canon, metrics, placement, case)
        total = _total_score(breakdown)

        placements = [
            LayoutPlacement(instance_id=iid, row=placement[iid][0], x_hp=placement[iid][1])
            for iid in order
        ]

        return SuggestedLayout(
            rig_id=canon.rig_id,
            layout_type=layout_type,
            placements=placements,
            total_score=float(total),
            score_breakdown=breakdown,
            rationale=rationale,
            meta=_meta_derived(canon.rig_id),
        )

    beginner = build(
        LayoutType.beginner,
        _layout_order_beginner(canon, metrics),
        "Beginner: left→right teaching flow (clock/controllers → sources → shapers → routing → FX → IO).",
    )
    performance = build(
        LayoutType.performance,
        _layout_order_performance(canon, metrics),
        "Performance: prioritize touch-heavy modules (controllers/clocks/routers) for central access and tight control loops.",
    )
    experimental = build(
        LayoutType.experimental,
        _layout_order_experimental(canon, metrics),
        "Experimental: interleaved categories to encourage short generative feedback loops and rapid traversal.",
    )

    return [beginner, performance, experimental]
