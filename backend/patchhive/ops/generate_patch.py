from __future__ import annotations

from patchhive.schemas import (
    CableType,
    CanonicalRig,
    MacroControl,
    PatchCable,
    PatchGraph,
    PatchMacro,
    PatchPlan,
    PatchTimeline,
    TimelineSection,
    ValidationReport,
)


def generate_patch(
    rig: CanonicalRig,
    *,
    intent,
    seed: int,
) -> dict:
    """
    Deterministic patch generation placeholder for query surface tests.
    """
    patch_id = f"patch.{rig.rig_id}.{seed}"
    timeline = PatchTimeline(
        sections=[TimelineSection.prep, TimelineSection.peak, TimelineSection.seal]
    )
    cables = [PatchCable(type=CableType.audio), PatchCable(type=CableType.cv)]
    macros = [
        PatchMacro(
            macro_id="macro.main_intensity",
            controls=[MacroControl(range=(0.1, 0.7))],
        )
    ]

    patch = PatchGraph(
        patch_id=patch_id,
        rig_id=rig.rig_id,
        timeline=timeline,
        cables=cables,
        macros=macros,
    )
    plan = PatchPlan(intent=intent, warnings=[])
    validation = ValidationReport(ok=True, warnings=[])
    return {"patch": patch, "plan": plan, "validation": validation, "variations": []}
