"""Patch fingerprint computation."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from modules.models import Module

from .models import ComplexityVector, DominantRoles, PatchFingerprint
from .patching_order import TIME_TYPES, VOICE_TYPES, MOD_TYPES, PROB_TYPES, PERF_TYPES


def _compute_topology_hash(connections: list[dict[str, Any]]) -> str:
    """Compute stable hash of patch topology."""
    edges = []
    for conn in connections:
        from_id = conn.get("from_module_id", 0)
        from_port = conn.get("from_port", "")
        to_id = conn.get("to_module_id", 0)
        to_port = conn.get("to_port", "")
        cable_type = conn.get("cable_type", "")
        edges.append(f"{from_id}:{from_port}->{to_id}:{to_port}:{cable_type}")

    canonical = "|".join(sorted(edges))
    return sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _has_feedback_cycle(connections: list[dict[str, Any]]) -> bool:
    """Detect feedback loops in connection graph."""
    graph: dict[int, set[int]] = {}
    for conn in connections:
        from_id = conn.get("from_module_id")
        to_id = conn.get("to_module_id")
        if from_id and to_id:
            if from_id not in graph:
                graph[from_id] = set()
            graph[from_id].add(to_id)

    visited = set()
    rec_stack = set()

    def has_cycle(node: int) -> bool:
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            if has_cycle(node):
                return True
    return False


def _compute_complexity_vector(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> ComplexityVector:
    """Compute patch complexity metrics."""
    cable_count = len(connections)

    unique_jacks = set()
    modulation_sources = set()
    probability_loci = set()

    for conn in connections:
        from_id = conn.get("from_module_id")
        to_id = conn.get("to_module_id")
        from_port = conn.get("from_port", "")
        to_port = conn.get("to_port", "")

        unique_jacks.add((from_id, from_port, "out"))
        unique_jacks.add((to_id, to_port, "in"))

        from_module = modules.get(from_id)
        if from_module:
            from_type = (from_module.module_type or "").upper()
            if from_type in MOD_TYPES:
                modulation_sources.add(from_id)
            if from_type in PROB_TYPES:
                probability_loci.add(from_id)

    feedback_present = _has_feedback_cycle(connections)

    return ComplexityVector(
        cable_count=cable_count,
        unique_jack_count=len(unique_jacks),
        modulation_source_count=len(modulation_sources),
        probability_locus_count=len(probability_loci),
        feedback_present=feedback_present,
    )


def _compute_dominant_roles(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> DominantRoles:
    """Compute distribution of module roles."""
    role_counts = {
        "time": 0,
        "voice": 0,
        "modulation": 0,
        "probability": 0,
        "gesture": 0,
    }

    involved_modules = set()
    for conn in connections:
        involved_modules.add(conn.get("from_module_id"))
        involved_modules.add(conn.get("to_module_id"))

    for module_id in involved_modules:
        module = modules.get(module_id)
        if not module:
            continue
        module_type = (module.module_type or "").upper()

        if module_type in TIME_TYPES:
            role_counts["time"] += 1
        elif module_type in VOICE_TYPES:
            role_counts["voice"] += 1
        elif module_type in MOD_TYPES:
            role_counts["modulation"] += 1
        elif module_type in PROB_TYPES:
            role_counts["probability"] += 1
        elif module_type in PERF_TYPES:
            role_counts["gesture"] += 1

    total = sum(role_counts.values()) or 1

    return DominantRoles(
        time_pct=round(100 * role_counts["time"] / total, 1),
        voice_pct=round(100 * role_counts["voice"] / total, 1),
        modulation_pct=round(100 * role_counts["modulation"] / total, 1),
        probability_pct=round(100 * role_counts["probability"] / total, 1),
        gesture_pct=round(100 * role_counts["gesture"] / total, 1),
    )


def _compute_rack_fit_score(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> float | None:
    """Compute rack fit score based on cable distances."""
    # This is a simplified version - real implementation would use actual rack positions
    # For now, return None if we don't have position data
    return None


def compute_patch_fingerprint(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> PatchFingerprint:
    """Compute complete patch fingerprint."""
    topology_hash = _compute_topology_hash(connections)
    complexity_vector = _compute_complexity_vector(connections, modules)
    dominant_roles = _compute_dominant_roles(connections, modules)
    rack_fit_score = _compute_rack_fit_score(connections, modules)

    return PatchFingerprint(
        topology_hash=topology_hash,
        complexity_vector=complexity_vector,
        dominant_roles=dominant_roles,
        rack_fit_score=rack_fit_score,
    )
