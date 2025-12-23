"""Performance macro computation."""

from __future__ import annotations

from typing import Any

from modules.models import Module

from .models import PerformanceMacroCard
from .patching_order import PERF_TYPES, VOICE_TYPES, MOD_TYPES


def _identify_performance_modules(modules: dict[int, Module]) -> list[Module]:
    """Identify modules suitable for performance control."""
    perf_modules = []

    for module in modules.values():
        module_type = (module.module_type or "").upper()
        if module_type in PERF_TYPES:
            perf_modules.append(module)

    return perf_modules


def _generate_macro_for_module(
    module: Module,
    connections: list[dict[str, Any]],
    all_modules: dict[int, Module],
) -> PerformanceMacroCard | None:
    """Generate a performance macro for a specific module."""
    module_id = module.id

    # Find downstream connections
    downstream = [
        conn for conn in connections if conn.get("from_module_id") == module_id
    ]

    if not downstream:
        return None

    controls_involved = [f"{module.name} output"]
    affected_modules = set()

    for conn in downstream:
        to_id = conn.get("to_module_id")
        to_module = all_modules.get(to_id)
        if to_module:
            affected_modules.add(to_module.name)
            controls_involved.append(
                f"{module.name} {conn.get('from_port', '')} → {to_module.name}"
            )

    if not affected_modules:
        return None

    macro_id = f"macro_{module.name.lower().replace(' ', '_')}"
    expected_effect = f"Control {', '.join(sorted(affected_modules))}"
    safe_bounds = "Start at 50%, adjust ±30% for variation"
    risk_level = "Low"

    return PerformanceMacroCard(
        macro_id=macro_id,
        controls_involved=controls_involved[:3],  # Limit to top 3
        expected_effect=expected_effect,
        safe_bounds=safe_bounds,
        risk_level=risk_level,
    )


def _generate_voice_macro(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> PerformanceMacroCard | None:
    """Generate a macro for voice/timbre control."""
    voice_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in VOICE_TYPES
    ]

    if not voice_modules:
        return None

    controls = []
    for vm in voice_modules[:2]:
        controls.append(f"{vm.name} pitch/timbre")

    return PerformanceMacroCard(
        macro_id="macro_voice_morph",
        controls_involved=controls,
        expected_effect="Shift voice character and harmonic content",
        safe_bounds="Adjust pitch ±2 octaves, timbre 20-80%",
        risk_level="Medium",
    )


def _generate_modulation_macro(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> PerformanceMacroCard | None:
    """Generate a macro for modulation intensity."""
    mod_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in MOD_TYPES
    ]

    if not mod_modules:
        return None

    controls = []
    for mm in mod_modules[:2]:
        controls.append(f"{mm.name} depth/rate")

    return PerformanceMacroCard(
        macro_id="macro_mod_intensity",
        controls_involved=controls,
        expected_effect="Increase/decrease modulation depth globally",
        safe_bounds="Start at 30%, increase to 70% for dramatic effect",
        risk_level="High",
    )


def compute_performance_macros(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> list[PerformanceMacroCard]:
    """Compute performance macro suggestions."""
    macros = []

    # Try module-specific macros first
    perf_modules = _identify_performance_modules(modules)
    for module in perf_modules[:2]:  # Limit to 2 module-specific macros
        macro = _generate_macro_for_module(module, connections, modules)
        if macro:
            macros.append(macro)

    # Add voice macro if applicable
    voice_macro = _generate_voice_macro(connections, modules)
    if voice_macro:
        macros.append(voice_macro)

    # Add modulation macro if applicable
    mod_macro = _generate_modulation_macro(connections, modules)
    if mod_macro:
        macros.append(mod_macro)

    return macros[:4]  # Maximum 4 macros
