"""Deterministic scoring for rack layout recommendations."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ConnectionFrequency, LayoutScore, ModuleSpec

ZONE_ORDER = ["time", "voice", "mod", "fx", "utility", "performance"]

ROLE_ALIASES = {
    "clock": "time",
    "sequencer": "time",
    "trigger": "time",
    "gate": "time",
    "osc": "voice",
    "vco": "voice",
    "vcf": "voice",
    "vca": "voice",
    "audio": "voice",
    "lfo": "mod",
    "envelope": "mod",
    "env": "mod",
    "random": "mod",
    "fx": "fx",
    "effect": "fx",
    "mixer": "utility",
    "utility": "utility",
    "performance": "performance",
    "controller": "performance",
    "touch": "performance",
}


@dataclass
class LayoutMetrics:
    positions: dict[int, float]
    widths: dict[int, int]


def _normalize_role(tag: str) -> str:
    return ROLE_ALIASES.get(tag.lower(), tag.lower())


def build_layout_metrics(layout: list[int], modules: dict[int, ModuleSpec]) -> LayoutMetrics:
    positions: dict[int, float] = {}
    widths: dict[int, int] = {}
    cursor = 0
    for module_id in layout:
        module = modules[module_id]
        widths[module_id] = module.hp
        center = cursor + module.hp / 2
        positions[module_id] = center
        cursor += module.hp
    return LayoutMetrics(positions=positions, widths=widths)


def adjacency_score(
    layout: list[int],
    modules: dict[int, ModuleSpec],
    connections: list[ConnectionFrequency],
) -> float:
    if not connections:
        return 0.0
    metrics = build_layout_metrics(layout, modules)
    score = 0.0
    for conn in connections:
        if conn.from_module_id not in metrics.positions or conn.to_module_id not in metrics.positions:
            continue
        dist = abs(metrics.positions[conn.from_module_id] - metrics.positions[conn.to_module_id])
        score += conn.weight / (1 + dist)
    return score


def zoning_score(layout: list[int], modules: dict[int, ModuleSpec]) -> float:
    if not layout:
        return 0.0
    role_targets = {role: idx for idx, role in enumerate(ZONE_ORDER)}
    ideal_positions = []
    actual_positions = []

    for idx, module_id in enumerate(layout):
        tags = modules[module_id].role_tags
        normalized = [_normalize_role(tag) for tag in tags]
        role = next((tag for tag in normalized if tag in role_targets), "utility")
        ideal_positions.append(role_targets[role])
        actual_positions.append(idx / max(len(layout) - 1, 1))

    max_role = max(role_targets.values()) or 1
    ideal_norm = [role / max_role for role in ideal_positions]
    deltas = [abs(i - a) for i, a in zip(ideal_norm, actual_positions)]
    return 1 - (sum(deltas) / len(deltas))


def access_score(layout: list[int], modules: dict[int, ModuleSpec]) -> float:
    if not layout:
        return 0.0
    edge_count = max(1, len(layout) // 4)
    edge_indices = set(range(edge_count)) | set(range(len(layout) - edge_count, len(layout)))
    score = 0.0
    perf_modules = 0
    for idx, module_id in enumerate(layout):
        tags = [_normalize_role(tag) for tag in modules[module_id].role_tags]
        if "performance" in tags:
            perf_modules += 1
            score += 1.0 if idx in edge_indices else 0.4
    if perf_modules == 0:
        return 0.3
    return score / perf_modules


def cable_length_score(
    layout: list[int],
    modules: dict[int, ModuleSpec],
    connections: list[ConnectionFrequency],
) -> float:
    if not connections:
        return 0.0
    metrics = build_layout_metrics(layout, modules)
    distances = []
    for conn in connections:
        if conn.from_module_id not in metrics.positions or conn.to_module_id not in metrics.positions:
            continue
        distances.append(abs(metrics.positions[conn.from_module_id] - metrics.positions[conn.to_module_id]))
    if not distances:
        return 0.0
    avg_distance = sum(distances) / len(distances)
    return 1 / (1 + avg_distance)


def score_layout(
    layout: list[int],
    modules: dict[int, ModuleSpec],
    connections: list[ConnectionFrequency],
) -> LayoutScore:
    adjacency = adjacency_score(layout, modules, connections)
    zoning = zoning_score(layout, modules)
    access = access_score(layout, modules)
    cable = cable_length_score(layout, modules, connections)

    total = (adjacency * 0.35) + (zoning * 0.25) + (access * 0.2) + (cable * 0.2)
    return LayoutScore(
        adjacency_score=adjacency,
        zoning_score=zoning,
        access_score=access,
        cable_score=cable,
        total_score=total,
    )
