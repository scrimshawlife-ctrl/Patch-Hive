"""Deterministic patching order generator."""

from __future__ import annotations

from typing import Any

from modules.models import Module

from .models import PatchingOrder, PatchingStep

TIME_TYPES = {"CLOCK", "SEQUENCER", "TRIGGER", "GATE"}
VOICE_TYPES = {"VCO", "VCF", "VCA", "OSC", "OSCILLATOR"}
MOD_TYPES = {"LFO", "ENVELOPE", "ENV", "MOD"}
PROB_TYPES = {"RANDOM", "PROB", "PROBABILITY", "CONTROLLER", "TOUCH"}
PERF_TYPES = {"PERFORMANCE", "CONTROLLER", "TOUCH", "MACRO"}


def _module_type(module: Module | None) -> str:
    if not module or not module.module_type:
        return ""
    return module.module_type.upper()


def _connection_label(conn: dict[str, Any], modules: dict[int, Module]) -> str:
    from_module = modules.get(conn.get("from_module_id"))
    to_module = modules.get(conn.get("to_module_id"))
    from_name = from_module.name if from_module else "Unknown"
    to_name = to_module.name if to_module else "Unknown"
    return f"Patch {from_name} {conn.get('from_port', '')} -> {to_name} {conn.get('to_port', '')}".strip()


def _step_from_connections(
    step: int,
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
    label: str,
) -> PatchingStep:
    if connections:
        actions = "\n".join(_connection_label(conn, modules) for conn in connections)
        expected = f"{label} connections are active."
        fail_fast = "Verify the connected modules are present and ports match the wiring list."
    else:
        actions = f"No {label.lower()} connections detected."
        expected = f"{label} layer remains unchanged."
        fail_fast = "If a connection is expected, confirm module IDs and ports in the patch data."
    return PatchingStep(step=step, action=actions, expected_behavior=expected, fail_fast_check=fail_fast)


def generate_patching_order(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> PatchingOrder:
    """Generate Step 0-6 patching order from wiring data."""
    time_connections = []
    voice_connections = []
    mod_connections = []
    prob_connections = []

    for conn in connections:
        from_module = modules.get(conn.get("from_module_id"))
        to_module = modules.get(conn.get("to_module_id"))
        cable_type = (conn.get("cable_type") or "").lower()
        from_type = _module_type(from_module)
        to_type = _module_type(to_module)

        if cable_type in {"clock", "gate", "trigger"} or {
            "clock" in conn.get("from_port", "").lower(),
            "clock" in conn.get("to_port", "").lower(),
            "gate" in conn.get("from_port", "").lower(),
            "trigger" in conn.get("to_port", "").lower(),
        }:
            time_connections.append(conn)
        elif cable_type == "audio" or from_type in VOICE_TYPES or to_type in VOICE_TYPES:
            voice_connections.append(conn)
        elif cable_type == "cv" or from_type in MOD_TYPES or to_type in MOD_TYPES:
            mod_connections.append(conn)
        elif from_type in PROB_TYPES or to_type in PROB_TYPES:
            prob_connections.append(conn)

    used_module_names = sorted({modules[mid].name for mid in modules if mid in modules})
    if used_module_names:
        init_action = "Prepare modules: " + ", ".join(used_module_names)
    else:
        init_action = "No modules detected in patch data."

    init_step = PatchingStep(
        step=0,
        action=init_action,
        expected_behavior="Modules referenced by the patch are ready for cabling.",
        fail_fast_check="Confirm rack inventory matches the patch wiring list.",
    )

    step1 = _step_from_connections(1, time_connections, modules, "Time/Clock")
    step2 = _step_from_connections(2, voice_connections, modules, "Voice/Audio")
    step3 = _step_from_connections(3, mod_connections, modules, "Modulation")
    step4 = _step_from_connections(4, prob_connections, modules, "Probability/Gesture")

    stabilization_targets = voice_connections or mod_connections
    step5 = _step_from_connections(5, stabilization_targets, modules, "Stabilization")

    performance_modules = [
        module.name
        for module in modules.values()
        if _module_type(module) in PERF_TYPES
    ]
    if performance_modules:
        perf_action = "Define performance moves on: " + ", ".join(sorted(set(performance_modules)))
        perf_expected = "Performance controls respond as mapped."
        perf_fail_fast = "If controls do not respond, verify routing or MIDI/CV mappings."
    else:
        perf_action = "No explicit performance macros detected."
        perf_expected = "Performance layer remains neutral."
        perf_fail_fast = "If macros are expected, confirm module tags and connections."

    step6 = PatchingStep(
        step=6,
        action=perf_action,
        expected_behavior=perf_expected,
        fail_fast_check=perf_fail_fast,
    )

    steps = [init_step, step1, step2, step3, step4, step5, step6]
    return PatchingOrder(steps=steps)
