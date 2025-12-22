from __future__ import annotations

import hashlib
import random
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from patchhive.ops.validate_patch import validate_patch
from patchhive.schemas import (
    CableType,
    CanonicalRig,
    FieldMeta,
    FieldStatus,
    MacroControl,
    PatchCable,
    PatchGraph,
    PatchIntent,
    PatchMacro,
    PatchPlan,
    PatchTimeline,
    Provenance,
    ProvenanceType,
    SignalKind,
    TimelineSection,
)


class PatchGenError(Exception):
    pass


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _meta_derived(rig_id: str, seed: int, method: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=f"rig:{rig_id}:seed:{seed}",
                method=method,
            )
        ],
        confidence=0.85,
        status=FieldStatus.inferred,
    )


def _stable_patch_id(rig_id: str, archetype: str, seed: int) -> str:
    h = hashlib.sha256(f"{rig_id}|{archetype}|{seed}".encode("utf-8")).hexdigest()[:16]
    return f"patch.{rig_id}.{archetype}.{h}"


def _find_jack(canon: CanonicalRig, *, kind: SignalKind, dir_required: str) -> Optional[str]:
    """
    Find first jack matching (kind, direction) deterministically:
    - sort modules by instance_id
    - sort jacks by jack_id
    dir_required: "out" or "in"
    """
    modules = sorted(canon.modules, key=lambda m: m.instance_id)
    for m in modules:
        for j in sorted(m.jacks, key=lambda x: x.jack_id):
            if j.signal.kind != kind:
                continue
            if dir_required == "out" and j.dir.value in ("out", "bidir"):
                return j.jack_id
            if dir_required == "in" and j.dir.value in ("in", "bidir"):
                return j.jack_id
    return None


def _find_any_in(canon: CanonicalRig, acceptable: Tuple[SignalKind, ...]) -> Optional[str]:
    modules = sorted(canon.modules, key=lambda m: m.instance_id)
    for m in modules:
        for j in sorted(m.jacks, key=lambda x: x.jack_id):
            if j.signal.kind in acceptable and j.dir.value in ("in", "bidir"):
                return j.jack_id
    return None


def _cable_type_for(kind: SignalKind) -> CableType:
    return {
        SignalKind.audio: CableType.audio,
        SignalKind.pitch_cv: CableType.pitch_cv,
        SignalKind.gate: CableType.gate,
        SignalKind.trigger: CableType.trigger,
        SignalKind.clock: CableType.clock,
    }.get(kind, CableType.cv)


def _ritual_perform_steps() -> List[str]:
    return [
        "prep: set initial levels, confirm normals, start at conservative modulation depth.",
        "threshold: introduce first modulation route; bring the system to motion without chaos.",
        "peak: open the main macro; explore the patch’s primary transformation axis.",
        "release: reduce modulation depth; re-center pitch/clock; simplify the signal path.",
        "seal: return macros to baseline; stop clocks; document one lesson + one next experiment.",
    ]


def _build_macros(seed: int) -> List[PatchMacro]:
    # deterministic macro set (same seed => same ranges)
    rng = random.Random(seed)

    def jitter(a: float) -> float:
        return max(0.0, min(1.0, a + (rng.uniform(-0.05, 0.05))))

    macros: List[PatchMacro] = []
    macros.append(
        PatchMacro(
            macro_id="macro.main_intensity",
            controls=[
                MacroControl(
                    target="depth",
                    range=(jitter(0.2), jitter(0.9)),
                    meta=_meta_derived("macro", seed, "macro"),
                )
            ],
            meta=_meta_derived("macro", seed, "macro"),
        )
    )
    macros.append(
        PatchMacro(
            macro_id="macro.motion",
            controls=[
                MacroControl(
                    target="rate",
                    range=(jitter(0.1), jitter(0.8)),
                    meta=_meta_derived("macro", seed, "macro"),
                )
            ],
            meta=_meta_derived("macro", seed, "macro"),
        )
    )
    return macros


def generate_patch(
    canon: CanonicalRig,
    *,
    intent: PatchIntent,
    seed: int,
) -> dict:
    """
    Constrained v1 generator:
    Supported intent.archetype values:
      - "basic_voice"
      - "generative_mod"
      - "clocked_sequence"

    Returns dict:
      { "patch": PatchGraph, "plan": PatchPlan, "validation": ValidationReport, "variations": [PatchGraph, ...] }
    """
    archetype = intent.archetype.strip().lower()
    if archetype not in {"basic_voice", "generative_mod", "clocked_sequence"}:
        raise PatchGenError(f"Unsupported archetype: {intent.archetype}")

    patch_id = _stable_patch_id(canon.rig_id, archetype, seed)

    # Deterministic cable construction using available jacks.
    cables: List[PatchCable] = []

    # Common finds
    audio_out = _find_jack(canon, kind=SignalKind.audio, dir_required="out")
    audio_in = _find_any_in(canon, acceptable=(SignalKind.audio, SignalKind.cv_or_audio))
    cv_out = _find_jack(canon, kind=SignalKind.cv, dir_required="out") or _find_jack(
        canon, kind=SignalKind.lfo, dir_required="out"
    )
    cv_in = _find_any_in(canon, acceptable=(SignalKind.cv, SignalKind.cv_or_audio))
    clock_out = _find_jack(canon, kind=SignalKind.clock, dir_required="out")
    clock_in = _find_jack(canon, kind=SignalKind.clock, dir_required="in")

    meta = _meta_derived(canon.rig_id, seed, f"generate_patch.{archetype}.v1")

    if archetype == "basic_voice":
        # Minimal: audio out -> audio/cv_or_audio in (output or mixer input)
        if audio_out and audio_in:
            cables.append(
                PatchCable(from_jack=audio_out, to_jack=audio_in, type=CableType.audio, meta=meta)
            )
        else:
            # fallback: if only cv_or_audio out exists, treat as audio-ish
            cv_or_audio_out = _find_jack(canon, kind=SignalKind.cv_or_audio, dir_required="out")
            cv_or_audio_in = _find_any_in(canon, acceptable=(SignalKind.cv_or_audio, SignalKind.audio))
            if cv_or_audio_out and cv_or_audio_in:
                cables.append(
                    PatchCable(
                        from_jack=cv_or_audio_out,
                        to_jack=cv_or_audio_in,
                        type=CableType.audio,
                        meta=meta,
                    )
                )

    elif archetype == "generative_mod":
        # Audio path plus one modulation route.
        if audio_out and audio_in:
            cables.append(
                PatchCable(from_jack=audio_out, to_jack=audio_in, type=CableType.audio, meta=meta)
            )
        if cv_out and cv_in:
            cables.append(PatchCable(from_jack=cv_out, to_jack=cv_in, type=CableType.cv, meta=meta))

    elif archetype == "clocked_sequence":
        # Clock out -> clock in plus audio path.
        if clock_out and clock_in:
            cables.append(
                PatchCable(from_jack=clock_out, to_jack=clock_in, type=CableType.clock, meta=meta)
            )
        if audio_out and audio_in:
            cables.append(
                PatchCable(from_jack=audio_out, to_jack=audio_in, type=CableType.audio, meta=meta)
            )

    timeline = PatchTimeline(
        clock_bpm=120.0 if archetype == "clocked_sequence" else None,
        sections=[
            TimelineSection.prep,
            TimelineSection.threshold,
            TimelineSection.peak,
            TimelineSection.release,
            TimelineSection.seal,
        ],
        meta=meta,
    )

    macros = _build_macros(seed)

    patch = PatchGraph(
        patch_id=patch_id,
        rig_id=canon.rig_id,
        cables=cables,
        macros=macros,
        timeline=timeline,
        mode_selections=[],
        meta=meta,
    )

    plan = PatchPlan(
        patch_id=patch_id,
        intent=intent,
        setup=[
            "Confirm semi-normalled routes (if any) and decide which will remain intact.",
            "Start with all macro controls at minimum.",
            "Verify you have a clean output monitoring path before increasing levels.",
        ],
        perform=_ritual_perform_steps(),
        warnings=[
            "If the patch is silent, confirm audio path and output monitoring.",
            "If modulation causes instability, reduce depth and reintroduce slowly.",
        ],
        why_it_works=[
            "This patch is intentionally minimal: it establishes a stable signal path first, then adds motion.",
            "Ritual sequencing prevents runaway complexity and preserves learnability.",
        ],
        meta=meta,
    )

    validation = validate_patch(canon, patch)

    # Deterministic variations: tweak macro ranges + optionally swap modulation source if available
    variations: List[PatchGraph] = []
    # Variation 1: same cables, different macro seed
    v_seed = seed + 1
    v_patch = patch.model_copy(
        update={
            "patch_id": _stable_patch_id(canon.rig_id, f"{archetype}.var1", seed),
            "macros": _build_macros(v_seed),
            "meta": _meta_derived(canon.rig_id, v_seed, f"generate_patch.{archetype}.variation1.v1"),
        }
    )
    variations.append(v_patch)

    return {"patch": patch, "plan": plan, "validation": validation, "variations": variations}
