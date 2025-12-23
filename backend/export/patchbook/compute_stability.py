"""Patch stability analysis computation."""

from __future__ import annotations

from typing import Any

from modules.models import Module

from .models import StabilityEnvelope
from .patching_order import TIME_TYPES, VOICE_TYPES, MOD_TYPES


def _classify_stability(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
    has_feedback: bool,
) -> str:
    """Classify patch stability."""
    if has_feedback:
        return "Wild"

    modulation_count = 0
    for conn in connections:
        cable_type = (conn.get("cable_type") or "").lower()
        from_module = modules.get(conn.get("from_module_id"))
        from_type = (from_module.module_type or "").upper() if from_module else ""

        if cable_type == "cv" or from_type in MOD_TYPES:
            modulation_count += 1

    if modulation_count > 5:
        return "Sensitive"
    return "Stable"


def _identify_instability_sources(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
    has_feedback: bool,
) -> list[str]:
    """Identify primary instability sources."""
    sources = []

    if has_feedback:
        sources.append("Feedback loops detected in signal path")

    # Check for missing clocks
    has_clock = False
    for conn in connections:
        cable_type = (conn.get("cable_type") or "").lower()
        if cable_type in {"clock", "gate", "trigger"}:
            has_clock = True
            break

    time_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in TIME_TYPES
    ]
    if time_modules and not has_clock:
        sources.append("Time-based modules present but no clock connections found")

    # Check for high modulation density
    cv_count = sum(
        1 for conn in connections if (conn.get("cable_type") or "").lower() == "cv"
    )
    if cv_count > 5:
        sources.append(f"High CV density ({cv_count} modulation cables)")

    # Check for unconnected VCAs (common mistake)
    vca_modules = [
        m for m in modules.values() if "VCA" in (m.module_type or "").upper()
    ]
    for vca in vca_modules:
        vca_id = vca.id
        has_cv_input = any(
            conn.get("to_module_id") == vca_id
            and (conn.get("cable_type") or "").lower() == "cv"
            for conn in connections
        )
        if not has_cv_input:
            sources.append(f"{vca.name} has no CV control (may be silent)")

    if not sources:
        sources.append("No significant instability sources detected")

    return sources


def _generate_safe_start_ranges(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
    parameters: dict[str, dict[str, str]],
) -> list[str]:
    """Generate safe parameter starting ranges."""
    suggestions = []

    # VCA levels
    vca_modules = [
        m for m in modules.values() if "VCA" in (m.module_type or "").upper()
    ]
    if vca_modules:
        suggestions.append("VCA levels: Start at 50-70% (12-2 o'clock)")

    # VCO pitch tracking
    vco_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in VOICE_TYPES
    ]
    if vco_modules:
        suggestions.append("VCO FM depth: Start at 0-20% to avoid detuning")

    # LFO rates
    lfo_modules = [
        m for m in modules.values() if "LFO" in (m.module_type or "").upper()
    ]
    if lfo_modules:
        suggestions.append("LFO rates: Start slow (1-5Hz) and increase gradually")

    if not suggestions:
        suggestions.append("No critical parameters identified")

    return suggestions[:3]  # Top 3


def _generate_recovery_procedure(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
    stability_class: str,
) -> list[str]:
    """Generate recovery procedure for unstable patches."""
    if stability_class == "Stable":
        return [
            "Patch is stable",
            "If issues occur, check cable connections first",
            "Verify all modules are powered and initialized",
        ]

    procedure = []

    if stability_class == "Wild":
        procedure.append("STEP 1: Reduce all VCA/mixer levels to zero")
        procedure.append("STEP 2: Slowly raise master VCA to 50%")
        procedure.append("STEP 3: Add modulation sources one at a time")

    procedure.extend(
        [
            f"STEP {len(procedure) + 1}: Check clock/gate signals are present",
            f"STEP {len(procedure) + 2}: Verify envelope generators are triggering",
            f"STEP {len(procedure) + 3}: Confirm filter cutoff is not fully closed",
        ]
    )

    return procedure


def compute_stability_envelope(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
    parameters: dict[str, dict[str, str]],
    has_feedback: bool = False,
) -> StabilityEnvelope:
    """Compute stability envelope for a patch."""
    stability_class = _classify_stability(connections, modules, has_feedback)
    instability_sources = _identify_instability_sources(
        connections, modules, has_feedback
    )
    safe_ranges = _generate_safe_start_ranges(connections, modules, parameters)
    recovery = _generate_recovery_procedure(connections, modules, stability_class)

    return StabilityEnvelope(
        stability_class=stability_class,
        primary_instability_sources=instability_sources,
        safe_start_ranges=safe_ranges,
        recovery_procedure=recovery,
    )
