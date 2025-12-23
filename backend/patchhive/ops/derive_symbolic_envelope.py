from __future__ import annotations

from datetime import datetime, timezone

from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    PatchGraph,
    PatchPlan,
    Provenance,
    ProvenanceType,
    SymbolicPatchEnvelope,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta_derived(patch_id: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=f"patch:{patch_id}",
                method="derive_symbolic_envelope.v1",
            )
        ],
        confidence=0.85,
        status=FieldStatus.inferred,
    )


def derive_symbolic_envelope(patch: PatchGraph, plan: PatchPlan) -> SymbolicPatchEnvelope:
    """
    Purely mechanical projection from PatchGraph/PatchPlan into a compact envelope.
    """
    sections = [s.value for s in patch.timeline.sections]
    has_seal = "seal" in sections

    curve_map = {"prep": 0.15, "threshold": 0.45, "peak": 0.95, "release": 0.55, "seal": 0.10}
    temporal = [curve_map.get(s, 0.3) for s in sections]

    non_audio = sum(1 for c in patch.cables if c.type.value != "audio")
    cable_term = min(1.0, non_audio / 6.0)

    depth = 0.4
    for macro in patch.macros:
        if macro.macro_id == "macro.main_intensity" and macro.controls:
            a, b = macro.controls[0].range
            depth = max(0.0, min(1.0, abs(b - a)))
            break

    chaos = [
        max(0.0, min(1.0, (0.35 * x) + (0.35 * depth) + (0.30 * cable_term)))
        for x in temporal
    ]

    macro_n = len(patch.macros)
    cable_n = len(patch.cables)
    performer = max(0.0, min(1.0, 0.55 + 0.08 * macro_n - 0.03 * cable_n))
    automation = max(0.0, min(1.0, 1.0 - performer))

    warning_penalty = min(0.6, 0.1 * len(plan.warnings))
    closure = (0.9 if has_seal else 0.4) - warning_penalty
    closure = max(0.0, min(1.0, closure))

    archetype_key = plan.intent.archetype.strip().lower()
    arche = {
        "basic_voice": {"Voice": 1.0},
        "generative_mod": {"Generator": 0.8, "Modulator": 0.6},
        "clocked_sequence": {"Clockwright": 0.9, "Sequencer": 0.7},
    }.get(archetype_key, {"Unknown": 1.0})

    return SymbolicPatchEnvelope(
        patch_id=patch.patch_id,
        archetype_vector=arche,
        temporal_intensity_curve=temporal,
        chaos_modulation_curve=chaos,
        agency_distribution={"performer": performer, "automation": automation},
        closure_strength=float(closure),
        meta=_meta_derived(patch.patch_id),
    )
