"""Generate patches for a canonical rig."""

from __future__ import annotations

import random

from patchhive.schemas import (
    JackSignalType,
    PatchEdge,
    PatchGraph,
    PatchMacro,
    PatchNode,
    PatchPlan,
    PatchStep,
    PatchTimelinePhase,
    Provenance,
    ProvenanceType,
)


def generate_patch_v1(
    rig_id: str,
    intent: str,
    seed: int,
    module_ids: list[str],
    normalled_edges: list,
) -> tuple[PatchGraph, PatchPlan, list[PatchGraph]]:
    rng = random.Random(seed)
    nodes = [PatchNode(node_id=f"node-{idx}", module_id=module_id) for idx, module_id in enumerate(module_ids)]
    edges: list[PatchEdge] = []
    for idx in range(max(0, len(nodes) - 1)):
        edges.append(
            PatchEdge(
                edge_id=f"edge-{idx}",
                from_jack=f"{nodes[idx].node_id}:out",
                to_jack=f"{nodes[idx + 1].node_id}:in",
                signal_type=JackSignalType.CV,
                provenance=Provenance(type=ProvenanceType.DERIVED),
            )
        )
    macros = [
        PatchMacro(
            macro_id="macro-flow",
            label="Flow",
            description="Establish modulation flow across the rig.",
            nodes=[node.node_id for node in nodes],
        )
    ]
    timeline = [
        PatchTimelinePhase(phase_id="prep", description="Initialize levels and route silence-safe.") ,
        PatchTimelinePhase(phase_id="threshold", description="Introduce first modulation threshold."),
        PatchTimelinePhase(phase_id="peak", description="Drive the peak interaction."),
        PatchTimelinePhase(phase_id="release", description="Ease modulation and dynamics."),
        PatchTimelinePhase(phase_id="seal", description="Seal the patch and document positions."),
    ]
    graph = PatchGraph(
        rig_id=rig_id,
        nodes=nodes,
        edges=edges,
        normalled_edges=normalled_edges,
        macros=macros,
        timeline=timeline,
        node_state={},
    )
    steps = [
        PatchStep(phase_id=phase.phase_id, instruction=phase.description) for phase in timeline
    ]
    plan = PatchPlan(rig_id=rig_id, intent=intent, steps=steps, closure=timeline)
    variations = []
    for index in range(2):
        variation_seed = seed + index + 1
        rng = random.Random(variation_seed)
        variation_edges = list(edges)
        if variation_edges:
            edge_index = rng.randrange(len(variation_edges))
            variation_edges[edge_index] = variation_edges[edge_index].model_copy(
                update={"signal_type": JackSignalType.AUDIO}
            )
        variations.append(
            graph.model_copy(update={"edges": variation_edges, "rig_id": rig_id})
        )
    return graph, plan, variations
