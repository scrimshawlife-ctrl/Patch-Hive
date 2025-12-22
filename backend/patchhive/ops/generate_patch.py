"""Patch generation pipeline."""
from __future__ import annotations

import random
from typing import Dict, List, Tuple

from core.discovery import register_function
from patchhive.schemas import (
    CanonicalRig,
    PatchGraph,
    PatchPlan,
    PatchPlanSection,
    PatchNode,
    PatchCable,
    ValidationReport,
    SymbolicPatchEnvelope,
)
from patchhive.ops.validate_patch import validate_patch


def _select_by_category(canonical_rig: CanonicalRig, category: str) -> List[str]:
    return [
        module.stable_id
        for module in canonical_rig.modules
        if category in module.capability_categories
    ]


def _build_patch_graph(canonical_rig: CanonicalRig, seed: int) -> PatchGraph:
    rng = random.Random(seed)
    nodes = [
        PatchNode(module_id=module.stable_id, label=module.gallery_entry.name)
        for module in canonical_rig.modules
    ]
    sources = _select_by_category(canonical_rig, "Sources")
    shapers = _select_by_category(canonical_rig, "Shapers")
    routers = _select_by_category(canonical_rig, "Routers / Mix")
    controllers = _select_by_category(canonical_rig, "Controllers")
    modulators = _select_by_category(canonical_rig, "Modulators")

    cables: List[PatchCable] = []
    if sources and shapers:
        cables.append(
            PatchCable(
                from_module_id=sources[0],
                from_port="out",
                to_module_id=shapers[0],
                to_port="in",
                cable_type="audio",
            )
        )
    if shapers and routers:
        cables.append(
            PatchCable(
                from_module_id=shapers[0],
                from_port="out",
                to_module_id=routers[0],
                to_port="in",
                cable_type="audio",
            )
        )
    if modulators and shapers:
        cables.append(
            PatchCable(
                from_module_id=modulators[0],
                from_port="out",
                to_module_id=shapers[0],
                to_port="cv",
                cable_type="cv",
            )
        )
    if controllers and modulators:
        cables.append(
            PatchCable(
                from_module_id=controllers[0],
                from_port="gate",
                to_module_id=modulators[0],
                to_port="sync",
                cable_type="gate",
            )
        )
    rng.shuffle(cables)

    mode_selections: Dict[str, str] = {}
    for module in canonical_rig.modules:
        if module.gallery_entry.modes:
            mode_selections[module.stable_id] = module.gallery_entry.modes[0].name

    return PatchGraph(
        nodes=nodes,
        cables=cables,
        macros=["drone swell", "timbral shift"],
        timeline=["prep", "threshold", "peak", "release", "seal"],
        mode_selections=mode_selections,
    )


def _build_patch_plan() -> PatchPlan:
    perform = [
        PatchPlanSection(name="prep", actions=["tune sources", "set initial gains"]),
        PatchPlanSection(name="threshold", actions=["introduce modulation", "open VCAs"]),
        PatchPlanSection(name="peak", actions=["maximize cross-modulation", "push resonance"]),
        PatchPlanSection(name="release", actions=["reduce modulation depth", "soften filters"]),
        PatchPlanSection(name="seal", actions=["return to steady state", "confirm silence floor"]),
    ]
    return PatchPlan(
        intent="Create a deterministic, evolving patch traversal.",
        setup=["Verify power rails", "Align clock domain", "Confirm normals"],
        perform=perform,
        warnings=["Seal step is mandatory to stabilize the ritual."],
        why_it_works="Structured modulation keeps chaos bounded while preserving motion.",
    )


def _build_symbolic_envelope(patch_graph: PatchGraph) -> SymbolicPatchEnvelope:
    intensity = [0.2, 0.5, 0.9, 0.4, 0.1]
    chaos_curve = [0.1, 0.4, 0.8, 0.3, 0.1]
    archetype_vector = {
        "architect": 0.4,
        "alchemist": 0.3,
        "trickster": 0.2,
        "seer": 0.1,
    }
    agency_distribution = {"system": 0.6, "performer": 0.4}
    closure_strength = 0.9 if "seal" in patch_graph.timeline else 0.0
    return SymbolicPatchEnvelope(
        archetype_vector=archetype_vector,
        temporal_intensity_curve=intensity,
        chaos_modulation_curve=chaos_curve,
        agency_distribution=agency_distribution,
        closure_strength=closure_strength,
    )


def generate_patch(
    canonical_rig: CanonicalRig,
    seed: int = 0,
) -> Tuple[PatchGraph, PatchPlan, ValidationReport, List[PatchGraph], SymbolicPatchEnvelope]:
    patch_graph = _build_patch_graph(canonical_rig, seed=seed)
    patch_plan = _build_patch_plan()
    validation = validate_patch(patch_graph, canonical_rig)
    variation = _build_patch_graph(canonical_rig, seed=seed + 1)
    envelope = _build_symbolic_envelope(patch_graph)
    return patch_graph, patch_plan, validation, [variation], envelope


register_function(
    name="generate_patch",
    function=generate_patch,
    description="Generate PatchGraph, PatchPlan, ValidationReport, and variations.",
    input_model="CanonicalRig, seed",
    output_model="PatchGraph, PatchPlan, ValidationReport, List[PatchGraph], SymbolicPatchEnvelope",
)
