"""Computed PatchBook panel helpers."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any, Iterable

from .models import (
    ComplexityVector,
    DominantRoles,
    ParameterDelta,
    PatchFingerprint,
    PatchModulePosition,
    PatchVariant,
    PerformanceMacroCard,
    StabilityEnvelope,
    TroubleshootingDecisionTree,
    WiringDelta,
)


ROLE_KEYWORDS = {
    "time": {"clock", "tempo", "sync", "gate", "trigger", "trig"},
    "voice": {"audio", "osc", "vco", "voice", "signal", "out", "in"},
    "modulation": {"mod", "cv", "lfo", "env", "fm", "am", "depth", "rate"},
    "probability": {"prob", "chance", "rand", "random"},
    "gesture": {"touch", "press", "manual", "gesture", "pressure"},
}

MODULATION_KEYWORDS = ROLE_KEYWORDS["modulation"]
PROBABILITY_KEYWORDS = ROLE_KEYWORDS["probability"]
TIME_KEYWORDS = ROLE_KEYWORDS["time"]
GAIN_KEYWORDS = {"gain", "level", "amp", "volume", "drive", "res", "resonance", "feedback"}


@dataclass(frozen=True)
class PatchInsights:
    complexity: ComplexityVector
    modulation_sources: set[int]
    probability_loci: set[int]
    feedback_connections: list[dict[str, Any]]
    effort_score: int


def _normalized_tokens(text: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", text.lower()) if token}


def _matches_keywords(text: str, keywords: Iterable[str]) -> bool:
    tokens = _normalized_tokens(text)
    return any(keyword in tokens or keyword in text.lower() for keyword in keywords)


def _parse_numeric(value: str) -> float | None:
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _module_name_map(module_inventory: list[PatchModulePosition]) -> dict[int, str]:
    return {module.module_id: module.name for module in module_inventory}


def _build_topology_hash(connections: list[dict[str, Any]]) -> str:
    normalized = []
    for conn in connections:
        normalized.append(
            {
                "from_module_id": conn.get("from_module_id"),
                "from_port": conn.get("from_port", ""),
                "to_module_id": conn.get("to_module_id"),
                "to_port": conn.get("to_port", ""),
                "cable_type": conn.get("cable_type", ""),
            }
        )
    normalized = sorted(
        normalized,
        key=lambda item: (
            item.get("from_module_id") or 0,
            item.get("from_port", ""),
            item.get("to_module_id") or 0,
            item.get("to_port", ""),
            item.get("cable_type", ""),
        ),
    )
    digest = sha256(json.dumps(normalized, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
    return digest


def _collect_ports(connections: list[dict[str, Any]]) -> list[tuple[int | None, str]]:
    ports = []
    for conn in connections:
        ports.append((conn.get("from_module_id"), conn.get("from_port", "")))
        ports.append((conn.get("to_module_id"), conn.get("to_port", "")))
    return ports


def _dominant_roles(connections: list[dict[str, Any]], parameters: list[dict[str, str]]) -> DominantRoles:
    role_counts = {role: 0 for role in ROLE_KEYWORDS}
    for _, port in _collect_ports(connections):
        for role, keywords in ROLE_KEYWORDS.items():
            if _matches_keywords(port, keywords):
                role_counts[role] += 1
    for param in parameters:
        name = param.get("parameter", "")
        for role, keywords in ROLE_KEYWORDS.items():
            if _matches_keywords(name, keywords):
                role_counts[role] += 1

    total = sum(role_counts.values()) or 1
    return DominantRoles(
        time=round(role_counts["time"] * 100 / total, 1),
        voice=round(role_counts["voice"] * 100 / total, 1),
        modulation=round(role_counts["modulation"] * 100 / total, 1),
        probability=round(role_counts["probability"] * 100 / total, 1),
        gesture=round(role_counts["gesture"] * 100 / total, 1),
    )


def _rack_fit_score(
    connections: list[dict[str, Any]],
    module_inventory: list[PatchModulePosition],
) -> float | None:
    if not module_inventory:
        return None
    for module in module_inventory:
        if module.row_index is None or module.start_hp is None:
            return None
    positions = {
        module.module_id: (module.row_index or 0, (module.start_hp or 0) + module.hp / 2)
        for module in module_inventory
    }
    centers = [center for _, center in positions.values()]
    if not centers:
        return None
    max_span = max(centers) - min(centers) or 1
    distances = []
    row_hops = []
    for conn in connections:
        from_id = conn.get("from_module_id")
        to_id = conn.get("to_module_id")
        if from_id not in positions or to_id not in positions:
            continue
        from_row, from_center = positions[from_id]
        to_row, to_center = positions[to_id]
        distances.append(abs(from_center - to_center))
        row_hops.append(abs(from_row - to_row))
    if not distances:
        return 100.0
    avg_distance = sum(distances) / len(distances)
    avg_row_hop = sum(row_hops) / len(row_hops)
    score = 100 - (avg_distance / max_span) * 50 - avg_row_hop * 5
    return round(max(0.0, score), 1)


def compute_patch_fingerprint(
    connections: list[dict[str, Any]],
    parameters: list[dict[str, str]],
    module_inventory: list[PatchModulePosition],
    allow_rack_fit: bool,
) -> tuple[PatchFingerprint, PatchInsights]:
    ports = _collect_ports(connections)
    unique_jacks = {(module_id, port) for module_id, port in ports if module_id is not None and port}

    modulation_sources = {
        module_id
        for module_id, port in ports
        if module_id is not None and _matches_keywords(port, MODULATION_KEYWORDS)
    }
    probability_loci = {
        module_id
        for module_id, port in ports
        if module_id is not None and _matches_keywords(port, PROBABILITY_KEYWORDS)
    }
    feedback_connections = [
        conn
        for conn in connections
        if conn.get("from_module_id") and conn.get("from_module_id") == conn.get("to_module_id")
    ]

    complexity = ComplexityVector(
        cable_count=len(connections),
        unique_jack_count=len(unique_jacks),
        modulation_source_count=len(modulation_sources),
        probability_locus_count=len(probability_loci),
        feedback_present=bool(feedback_connections),
    )

    effort_score = int(
        min(
            100,
            complexity.cable_count * 6
            + complexity.modulation_source_count * 8
            + complexity.probability_locus_count * 10
            + (15 if complexity.feedback_present else 0),
        )
    )

    fingerprint = PatchFingerprint(
        topology_hash=_build_topology_hash(connections),
        complexity_vector=complexity,
        dominant_roles=_dominant_roles(connections, parameters),
        rack_fit_score=_rack_fit_score(connections, module_inventory) if allow_rack_fit else None,
    )
    return fingerprint, PatchInsights(
        complexity=complexity,
        modulation_sources=modulation_sources,
        probability_loci=probability_loci,
        feedback_connections=feedback_connections,
        effort_score=effort_score,
    )


def compute_stability_envelope(
    connections: list[dict[str, Any]],
    parameters: list[dict[str, str]],
    module_inventory: list[PatchModulePosition],
    insights: PatchInsights,
) -> StabilityEnvelope:
    instability_sources: list[str] = []
    module_names = _module_name_map(module_inventory)

    if insights.feedback_connections:
        first = insights.feedback_connections[0]
        module_id = first.get("from_module_id")
        module_name = module_names.get(module_id, "Unknown")
        instability_sources.append(f"Feedback path detected at {module_name}")
    if insights.probability_loci:
        instability_sources.append("Probability modulation present")
    if insights.modulation_sources and insights.complexity.cable_count > 4:
        instability_sources.append("High modulation density")
    if insights.complexity.cable_count > 10:
        instability_sources.append("Dense cabling")

    if insights.complexity.feedback_present or insights.probability_loci:
        stability_class = "Wild"
    elif insights.complexity.modulation_source_count > 1 or insights.complexity.cable_count > 6:
        stability_class = "Sensitive"
    else:
        stability_class = "Stable"

    safe_start_ranges = []
    for param in sorted(parameters, key=lambda item: (item.get("module_name", ""), item.get("parameter", ""))):
        if len(safe_start_ranges) >= 3:
            break
        safe_start_ranges.append(f"{param.get('module_name')} {param.get('parameter')}: {param.get('value')}")

    recovery_procedure: list[str] = []
    if insights.feedback_connections:
        for conn in insights.feedback_connections[:2]:
            recovery_procedure.append(
                "Remove feedback cable: "
                f"{module_names.get(conn.get('from_module_id'), 'Unknown')} "
                f"{conn.get('from_port', '')} → "
                f"{module_names.get(conn.get('to_module_id'), 'Unknown')} "
                f"{conn.get('to_port', '')}"
            )
    mod_params = [
        param
        for param in parameters
        if _matches_keywords(param.get("parameter", ""), MODULATION_KEYWORDS)
    ]
    if mod_params:
        names = ", ".join({param.get("parameter", "") for param in mod_params})
        recovery_procedure.append(f"Reduce modulation depth on: {names}")
    prob_params = [
        param
        for param in parameters
        if _matches_keywords(param.get("parameter", ""), PROBABILITY_KEYWORDS)
    ]
    if prob_params:
        details = ", ".join(
            f"{param.get('parameter')}={param.get('value')}" for param in prob_params
        )
        recovery_procedure.append(f"Return probability controls to snapshot values: {details}")

    return StabilityEnvelope(
        stability_class=stability_class,
        primary_instability_sources=instability_sources,
        safe_start_ranges=safe_start_ranges,
        recovery_procedure=recovery_procedure,
    )


def compute_troubleshooting_tree(
    connections: list[dict[str, Any]],
    parameters: list[dict[str, str]],
    module_inventory: list[PatchModulePosition],
) -> TroubleshootingDecisionTree:
    module_names = _module_name_map(module_inventory)

    def fmt(conn: dict[str, Any]) -> str:
        return (
            f"{module_names.get(conn.get('from_module_id'), 'Unknown')} {conn.get('from_port', '')} "
            f"→ {module_names.get(conn.get('to_module_id'), 'Unknown')} {conn.get('to_port', '')}"
        )

    no_sound_checks = [
        f"Confirm audio cable: {fmt(conn)}"
        for conn in connections
        if _matches_keywords(conn.get("cable_type", ""), {"audio"})
        or _matches_keywords(conn.get("from_port", ""), {"audio", "out"})
    ][:5]

    no_modulation_checks = [
        f"Confirm modulation cable: {fmt(conn)}"
        for conn in connections
        if _matches_keywords(conn.get("from_port", ""), MODULATION_KEYWORDS)
        or _matches_keywords(conn.get("to_port", ""), MODULATION_KEYWORDS)
    ][:5]

    timing_instability_checks = [
        f"Confirm clock/gate cable: {fmt(conn)}"
        for conn in connections
        if _matches_keywords(conn.get("from_port", ""), TIME_KEYWORDS)
        or _matches_keywords(conn.get("to_port", ""), TIME_KEYWORDS)
    ][:5]

    gain_staging_checks = [
        f"Verify {param.get('module_name')} {param.get('parameter')} at {param.get('value')}"
        for param in parameters
        if _matches_keywords(param.get("parameter", ""), GAIN_KEYWORDS)
    ][:5]

    return TroubleshootingDecisionTree(
        no_sound_checks=no_sound_checks,
        no_modulation_checks=no_modulation_checks,
        timing_instability_checks=timing_instability_checks,
        gain_staging_checks=gain_staging_checks,
    )


def compute_performance_macros(
    parameters: list[dict[str, str]],
) -> list[PerformanceMacroCard]:
    macros: list[PerformanceMacroCard] = []
    by_module: dict[str, list[dict[str, str]]] = {}
    for param in parameters:
        by_module.setdefault(param.get("module_name", ""), []).append(param)

    for module_name, params in sorted(by_module.items()):
        if not params:
            continue
        selected = sorted(params, key=lambda item: item.get("parameter", ""))[:2]
        control_names = [param.get("parameter", "") for param in selected]
        values = [param.get("value", "") for param in selected]
        numeric_values = [value for value in ([_parse_numeric(val) for val in values]) if value is not None]
        if numeric_values:
            base = sum(numeric_values) / len(numeric_values)
            safe_bounds = f"Keep within {base * 0.9:.2f}–{base * 1.1:.2f}"
        else:
            safe_bounds = "Stay near snapshot values"

        risk_level = "low"
        if any(_matches_keywords(name, {"feedback", "gain", "res", "drive"}) for name in control_names):
            risk_level = "high"
        elif any(_matches_keywords(name, {"level", "mix", "volume"}) for name in control_names):
            risk_level = "medium"

        macro_id = f"MACRO-{len(macros) + 1:02d}"
        macros.append(
            PerformanceMacroCard(
                macro_id=macro_id,
                controls_involved=control_names,
                expected_effect=f"Adjust {', '.join(control_names)} on {module_name}",
                safe_bounds=safe_bounds,
                risk_level=risk_level,
            )
        )
        if len(macros) >= 3:
            break
    return macros


def _parameter_delta(
    param: dict[str, str],
    factor: float,
) -> ParameterDelta | None:
    value = param.get("value", "")
    numeric = _parse_numeric(value)
    if numeric is None:
        return None
    to_value = numeric * factor
    return ParameterDelta(
        module_id=int(param.get("module_id", 0)),
        module_name=param.get("module_name", ""),
        parameter=param.get("parameter", ""),
        from_value=value,
        to_value=f"{to_value:.2f}",
    )


def compute_patch_variants(
    connections: list[dict[str, Any]],
    parameters: list[dict[str, str]],
    module_inventory: list[PatchModulePosition],
    insights: PatchInsights,
) -> list[PatchVariant]:
    variants: list[PatchVariant] = []
    module_names = _module_name_map(module_inventory)

    def wiring_delta(conn: dict[str, Any], action: str) -> WiringDelta:
        return WiringDelta(
            action=action,
            from_module=module_names.get(conn.get("from_module_id"), "Unknown"),
            from_port=conn.get("from_port", ""),
            to_module=module_names.get(conn.get("to_module_id"), "Unknown"),
            to_port=conn.get("to_port", ""),
            cable_type=conn.get("cable_type", ""),
        )

    stability_params = [
        param
        for param in parameters
        if _matches_keywords(param.get("parameter", ""), {"gain", "res", "resonance", "feedback", "drive"})
    ]
    stabilize_deltas = [
        delta
        for param in stability_params
        if (delta := _parameter_delta(param, 0.9)) is not None
    ]
    stabilize_wiring = [wiring_delta(conn, "remove") for conn in insights.feedback_connections]

    if stabilize_deltas or stabilize_wiring:
        summary_parts = []
        if stabilize_wiring:
            summary_parts.append("Removes feedback paths")
        if stabilize_deltas:
            summary_parts.append("Reduces gain/resonance")
        variants.append(
            PatchVariant(
                variant_type="stabilize",
                wiring_diff=stabilize_wiring,
                parameter_deltas=stabilize_deltas,
                behavioral_delta_summary="; ".join(summary_parts),
            )
        )

    wild_params = [
        param
        for param in parameters
        if _matches_keywords(param.get("parameter", ""), {"mod", "depth", "amount", "fm"})
    ]
    wild_deltas = [
        delta
        for param in wild_params
        if (delta := _parameter_delta(param, 1.1)) is not None
    ]
    if wild_deltas:
        variants.append(
            PatchVariant(
                variant_type="wild",
                wiring_diff=[],
                parameter_deltas=wild_deltas,
                behavioral_delta_summary="Increases modulation depth",
            )
        )

    performance_params = [
        param
        for param in parameters
        if _matches_keywords(param.get("parameter", ""), {"mix", "level", "balance", "pan"})
    ]
    performance_deltas = [
        delta
        for param in performance_params
        if (delta := _parameter_delta(param, 1.05)) is not None
    ]
    if performance_deltas:
        variants.append(
            PatchVariant(
                variant_type="performance",
                wiring_diff=[],
                parameter_deltas=performance_deltas,
                behavioral_delta_summary="Boosts performance-facing balance controls",
            )
        )

    return variants
