"""Troubleshooting decision tree computation."""

from __future__ import annotations

from typing import Any

from modules.models import Module

from .models import TroubleshootingTree
from .patching_order import TIME_TYPES, VOICE_TYPES


def _generate_no_sound_checks(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> list[str]:
    """Generate no-sound troubleshooting checks."""
    checks = []

    # Check for VCA presence
    vca_modules = [
        m for m in modules.values() if "VCA" in (m.module_type or "").upper()
    ]
    if vca_modules:
        vca_names = ", ".join(m.name for m in vca_modules[:2])
        checks.append(f"1. Verify {vca_names} level(s) are above 50%")

    # Check for audio path
    audio_cables = [
        conn for conn in connections if (conn.get("cable_type") or "").lower() == "audio"
    ]
    if audio_cables:
        checks.append("2. Confirm audio cables are seated firmly in jacks")

    # Check for oscillators
    voice_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in VOICE_TYPES
    ]
    if voice_modules:
        checks.append("3. Check oscillator pitch is in audible range (not too low/high)")

    checks.extend(
        [
            f"{len(checks) + 1}. Verify master output/mixer is turned up",
            f"{len(checks) + 1}. Check filter cutoff is not fully closed",
            f"{len(checks) + 1}. Confirm modules are receiving power (LEDs lit)",
        ]
    )

    return checks[:6]


def _generate_no_modulation_checks(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> list[str]:
    """Generate no-modulation troubleshooting checks."""
    checks = []

    cv_cables = [
        conn for conn in connections if (conn.get("cable_type") or "").lower() == "cv"
    ]

    if cv_cables:
        checks.append("1. Verify CV cables are patched to correct inputs")
        checks.append("2. Check LFO/envelope depth/attenuverter settings")

    checks.extend(
        [
            f"{len(checks) + 1}. Confirm modulation sources are running (check LEDs/lights)",
            f"{len(checks) + 1}. Test modulation source directly (patch to VCO pitch to hear it)",
            f"{len(checks) + 1}. Verify destination module responds to manual control first",
        ]
    )

    return checks[:5]


def _generate_timing_checks(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> list[str]:
    """Generate timing instability troubleshooting checks."""
    checks = []

    # Check for clock modules
    time_modules = [
        m for m in modules.values() if (m.module_type or "").upper() in TIME_TYPES
    ]
    if time_modules:
        checks.append("1. Verify clock source is running at expected tempo")
        checks.append("2. Check for clock division/multiplication settings")

    clock_cables = [
        conn
        for conn in connections
        if (conn.get("cable_type") or "").lower() in {"clock", "gate", "trigger"}
    ]
    if clock_cables:
        checks.append(f"{len(checks) + 1}. Confirm clock cables are not swapped with CV")

    checks.extend(
        [
            f"{len(checks) + 1}. Check for unintended feedback affecting timing",
            f"{len(checks) + 1}. Verify sequencer is not paused or in reset state",
        ]
    )

    return checks[:5]


def _generate_gain_staging_checks(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> list[str]:
    """Generate gain staging troubleshooting checks."""
    checks = [
        "1. Check that no stage is clipping (distortion not intended)",
        "2. Verify VCA/mixer channel levels are balanced",
        "3. Confirm output level is appropriate for destination (mixer/interface)",
        "4. Check for hot modulation sources overdriving inputs",
        "5. Test signal at each stage in chain to isolate problem",
    ]

    return checks


def compute_troubleshooting_tree(
    connections: list[dict[str, Any]],
    modules: dict[int, Module],
) -> TroubleshootingTree:
    """Compute troubleshooting decision tree."""
    no_sound = _generate_no_sound_checks(connections, modules)
    no_modulation = _generate_no_modulation_checks(connections, modules)
    timing = _generate_timing_checks(connections, modules)
    gain_staging = _generate_gain_staging_checks(connections, modules)

    return TroubleshootingTree(
        no_sound_checks=no_sound,
        no_modulation_checks=no_modulation,
        timing_instability_checks=timing,
        gain_staging_checks=gain_staging,
    )
