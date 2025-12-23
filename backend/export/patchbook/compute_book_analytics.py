"""Book-level analytics computation."""

from __future__ import annotations

from typing import Any

from modules.models import Module
from patches.models import Patch
from racks.models import RackModule

from .models import (
    CompatibilityReport,
    GoldenRackAnalysis,
    LearningPath,
    LearningPathStep,
    RackArrangement,
)


UTILITY_MODULES = {
    "VCA",
    "MIXER",
    "MULT",
    "ATTENUVERTER",
    "OFFSET",
    "SLEW",
    "INVERTER",
}


def _score_rack_arrangement(
    rack_modules: list[RackModule],
    modules: dict[int, Module],
    patches: list[Patch],
) -> float:
    """Score a rack arrangement based on cable proximity."""
    if not rack_modules or not patches:
        return 0.0

    # Build position map
    positions = {}
    for rm in rack_modules:
        positions[rm.module_id] = (rm.row_index, rm.start_hp)

    total_distance = 0
    connection_count = 0

    for patch in patches:
        for conn in patch.connections:
            from_id = conn.get("from_module_id")
            to_id = conn.get("to_module_id")

            if from_id in positions and to_id in positions:
                from_pos = positions[from_id]
                to_pos = positions[to_id]

                # Calculate Manhattan distance
                row_dist = abs(from_pos[0] - to_pos[0])
                hp_dist = abs(from_pos[1] - to_pos[1])
                distance = row_dist * 100 + hp_dist

                total_distance += distance
                connection_count += 1

    if connection_count == 0:
        return 100.0

    avg_distance = total_distance / connection_count
    # Normalize to 0-100 scale (lower distance = higher score)
    score = max(0, 100 - (avg_distance / 10))
    return round(score, 1)


def _identify_missing_utilities(
    rack_modules: list[RackModule],
    modules: dict[int, Module],
    patches: list[Patch],
) -> list[str]:
    """Identify missing utility modules."""
    present_types = set()
    for rm in rack_modules:
        module = modules.get(rm.module_id)
        if module:
            module_type = (module.module_type or "").upper()
            present_types.add(module_type)

    missing = []

    # Check for VCA
    if "VCA" not in present_types:
        has_audio = any(
            (conn.get("cable_type") or "").lower() == "audio"
            for patch in patches
            for conn in patch.connections
        )
        if has_audio:
            missing.append("VCA (for amplitude control)")

    # Check for mixer
    if "MIXER" not in present_types:
        audio_sources = set()
        for patch in patches:
            for conn in patch.connections:
                if (conn.get("cable_type") or "").lower() == "audio":
                    audio_sources.add(conn.get("from_module_id"))
        if len(audio_sources) > 2:
            missing.append("Mixer (for combining multiple audio sources)")

    # Check for attenuverter
    if "ATTENUVERTER" not in present_types and "OFFSET" not in present_types:
        cv_count = sum(
            1
            for patch in patches
            for conn in patch.connections
            if (conn.get("cable_type") or "").lower() == "cv"
        )
        if cv_count > 3:
            missing.append("Attenuverter/Offset (for CV control)")

    return missing


def compute_golden_rack_analysis(
    rack_modules: list[RackModule],
    modules: dict[int, Module],
    patches: list[Patch],
) -> GoldenRackAnalysis:
    """Compute golden rack arrangement analysis."""
    if not rack_modules:
        return GoldenRackAnalysis()

    score = _score_rack_arrangement(rack_modules, modules, patches)
    missing = _identify_missing_utilities(rack_modules, modules, patches)

    module_names = []
    for rm in sorted(rack_modules, key=lambda x: (x.row_index, x.start_hp)):
        module = modules.get(rm.module_id)
        if module:
            module_names.append(module.name)

    rationale = [
        f"Current arrangement scores {score}/100",
        f"Based on {len(patches)} patch(es) cable routing",
        "Modules ordered left-to-right, top-to-bottom",
    ]

    if score > 70:
        rationale.append("Efficient layout with short cable runs")
    elif score > 40:
        rationale.append("Moderate cable distances, some optimization possible")
    else:
        rationale.append("High cable distances, consider reorganizing")

    adjacency_summary = f"{len(module_names)} modules arranged across {max((rm.row_index for rm in rack_modules), default=0) + 1} row(s)"

    golden = RackArrangement(
        layout_id="current",
        modules_in_order=module_names,
        scoring_rationale=rationale[:5],
        adjacency_summary=adjacency_summary,
        missing_utility_warnings=missing,
    )

    return GoldenRackAnalysis(golden_arrangement=golden)


def compute_compatibility_report(
    rack_modules: list[RackModule],
    modules: dict[int, Module],
    patches: list[Patch],
) -> CompatibilityReport:
    """Compute compatibility and gap report."""
    missing = _identify_missing_utilities(rack_modules, modules, patches)

    workarounds = []
    for miss in missing[:3]:
        if "VCA" in miss:
            workarounds.append("Use mixer channel faders or manual volume control")
        elif "Mixer" in miss:
            workarounds.append("Stack audio using passive mults (with volume loss)")
        elif "Attenuverter" in miss:
            workarounds.append("Use module's built-in attenuators if available")

    warnings = []
    # Check for patches using modules not in rack
    for patch in patches:
        patch_module_ids = set()
        for conn in patch.connections:
            patch_module_ids.add(conn.get("from_module_id"))
            patch_module_ids.add(conn.get("to_module_id"))

        rack_module_ids = {rm.module_id for rm in rack_modules}
        missing_in_rack = patch_module_ids - rack_module_ids
        if missing_in_rack:
            warnings.append(
                f"Patch '{patch.name}' references modules not in current rack"
            )

    return CompatibilityReport(
        required_missing_utilities=missing,
        workaround_suggestions=workarounds,
        patch_compatibility_warnings=warnings,
    )


def compute_learning_path(
    patches: list[Patch],
    modules: dict[int, Module],
) -> LearningPath:
    """Compute ordered learning path."""
    if not patches:
        return LearningPath(steps=[])

    # Score patches by complexity
    patch_scores = []
    for patch in patches:
        cable_count = len(patch.connections)
        cv_count = sum(
            1
            for conn in patch.connections
            if (conn.get("cable_type") or "").lower() == "cv"
        )
        effort = cable_count + (cv_count * 1.5)
        patch_scores.append((patch, effort))

    # Sort by complexity (easiest first)
    patch_scores.sort(key=lambda x: x[1])

    steps = []
    seen_concepts = set()

    for idx, (patch, effort) in enumerate(patch_scores):
        concepts = []

        # Identify new concepts in this patch
        has_audio = any(
            (conn.get("cable_type") or "").lower() == "audio"
            for conn in patch.connections
        )
        has_cv = any(
            (conn.get("cable_type") or "").lower() == "cv"
            for conn in patch.connections
        )
        has_clock = any(
            (conn.get("cable_type") or "").lower() in {"clock", "gate"}
            for conn in patch.connections
        )

        if has_audio and "audio_routing" not in seen_concepts:
            concepts.append("Audio signal routing")
            seen_concepts.add("audio_routing")

        if has_cv and "cv_modulation" not in seen_concepts:
            concepts.append("CV modulation")
            seen_concepts.add("cv_modulation")

        if has_clock and "timing_sync" not in seen_concepts:
            concepts.append("Clock/timing synchronization")
            seen_concepts.add("timing_sync")

        if not concepts:
            concepts.append("Patch technique variation")

        steps.append(
            LearningPathStep(
                patch_id=patch.id,
                patch_name=patch.name,
                concepts_introduced=concepts,
                effort_score=round(effort, 1),
            )
        )

    return LearningPath(steps=steps)
