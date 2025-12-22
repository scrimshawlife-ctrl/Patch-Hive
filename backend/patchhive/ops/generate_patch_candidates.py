from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

from patchhive.schemas import (
    CableType,
    CanonicalRig,
    FieldMeta,
    FieldStatus,
    JackDir,
    MacroControl,
    PatchCable,
    PatchGraph,
    PatchMacro,
    PatchTimeline,
    Provenance,
    ProvenanceType,
    SignalKind,
    TimelineSection,
)
from patchhive.schemas_library import PatchSpaceConstraints
from patchhive.templates.registry import PatchTemplate


def _meta_derived(rig_id: str, method: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=datetime.now(timezone.utc),
                evidence_ref=f"rig:{rig_id}",
                method=method,
            )
        ],
        confidence=0.85,
        status=FieldStatus.inferred,
    )


def _stable_id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _cable_type(name: str) -> CableType:
    mapping = {
        "audio": CableType.audio,
        "cv": CableType.cv,
        "clock": CableType.clock,
        "gate": CableType.gate,
        "trigger": CableType.trigger,
        "pitch_cv": CableType.pitch_cv,
    }
    return mapping.get(name, CableType.cv)


def _build_macros(seed: int) -> List[PatchMacro]:
    return [
        PatchMacro(
            macro_id="macro.main_intensity",
            controls=[MacroControl(range=(0.1, 0.7))],
        )
    ]


def _jack_role_candidates(canon: CanonicalRig) -> Dict[str, List[str]]:
    """
    Build deterministic role buckets of jack_ids from CanonicalRig.
    """
    buckets: Dict[str, List[str]] = defaultdict(list)

    mods = sorted(canon.modules, key=lambda m: m.instance_id)
    for module in mods:
        jacks = sorted(module.jacks, key=lambda j: j.jack_id)
        for jack in jacks:
            is_out = jack.dir in (JackDir.out, JackDir.bidir)
            is_in = jack.dir in (JackDir.in_, JackDir.bidir)

            if is_out and jack.signal.kind in (SignalKind.audio, SignalKind.cv_or_audio):
                buckets["audio_out"].append(jack.jack_id)

            if is_in and jack.signal.kind in (SignalKind.audio, SignalKind.cv_or_audio):
                buckets["audio_in_or_cv_or_audio_in"].append(jack.jack_id)

            if is_out and jack.signal.kind in (
                SignalKind.cv,
                SignalKind.lfo,
                SignalKind.envelope,
                SignalKind.random,
                SignalKind.pitch_cv,
            ):
                buckets["cv_out"].append(jack.jack_id)

            if is_in and jack.signal.kind in (
                SignalKind.cv,
                SignalKind.cv_or_audio,
                SignalKind.lfo,
                SignalKind.envelope,
                SignalKind.random,
                SignalKind.pitch_cv,
            ):
                buckets["cv_in_or_cv_or_audio_in"].append(jack.jack_id)

            if is_out and jack.signal.kind == SignalKind.clock:
                buckets["clock_out"].append(jack.jack_id)
            if is_in and jack.signal.kind == SignalKind.clock:
                buckets["clock_in"].append(jack.jack_id)

    for key in list(buckets.keys()):
        buckets[key] = sorted(set(buckets[key]))
    return buckets


def _enumerate_assignments(
    template: PatchTemplate,
    role_buckets: Dict[str, List[str]],
    *,
    max_candidates: int,
) -> List[Dict[str, str]]:
    """
    Exhaustive cross-product enumeration with early caps.
    Returns list of role->jack_id assignments.
    """
    role_names = sorted(template.role_constraints.keys())
    per_role: List[tuple[str, List[str]]] = []
    for role in role_names:
        bucket_keys = template.role_constraints[role]
        cands: List[str] = []
        for bucket in bucket_keys:
            cands.extend(role_buckets.get(bucket, []))
        cands = sorted(set(cands))
        if not cands:
            return []
        per_role.append((role, cands))

    out: List[Dict[str, str]] = []

    def rec(i: int, cur: Dict[str, str]) -> None:
        if len(out) >= max_candidates:
            return
        if i >= len(per_role):
            if template.post_filter and not template.post_filter(cur):
                return
            out.append(dict(cur))
            return
        role, cands = per_role[i]
        for jack in cands:
            if jack in cur.values():
                continue
            cur[role] = jack
            rec(i + 1, cur)
            del cur[role]
            if len(out) >= max_candidates:
                return

    rec(0, {})
    return out


def _build_patch_from_assignment(
    canon: CanonicalRig,
    template: PatchTemplate,
    assign: Dict[str, str],
    seed: int,
) -> PatchGraph:
    patch_id = (
        f"patch.{canon.rig_id}.{template.template_id}."
        f"{_stable_id(canon.rig_id, template.template_id, str(seed), str(assign))}"
    )
    meta = _meta_derived(canon.rig_id, f"generate_patch_candidates:{template.template_id}")

    cables: List[PatchCable] = []
    for slot in template.slots:
        frm = assign[slot.role_out]
        to = assign[slot.role_in]
        cables.append(
            PatchCable(from_jack=frm, to_jack=to, type=_cable_type(slot.cable_type), meta=meta)
        )

    timeline = PatchTimeline(
        clock_bpm=120.0 if template.archetype == "clocked_sequence" else None,
        sections=[
            TimelineSection.prep,
            TimelineSection.threshold,
            TimelineSection.peak,
            TimelineSection.release,
            TimelineSection.seal,
        ],
        meta=meta,
    )

    return PatchGraph(
        patch_id=patch_id,
        rig_id=canon.rig_id,
        cables=cables,
        macros=_build_macros(seed),
        timeline=timeline,
        mode_selections=[],
        meta=meta,
    )


def generate_patch_candidates(
    canon: CanonicalRig,
    template: PatchTemplate,
    *,
    constraints: PatchSpaceConstraints,
    seed_base: int = 100,
) -> List[PatchGraph]:
    role_buckets = _jack_role_candidates(canon)
    assigns = _enumerate_assignments(
        template,
        role_buckets,
        max_candidates=constraints.max_candidates_per_template,
    )

    patches: List[PatchGraph] = []
    for idx, assignment in enumerate(assigns):
        seed = seed_base + idx
        patches.append(_build_patch_from_assignment(canon, template, assignment, seed=seed))
        if len(patches) >= constraints.keep_top_per_template:
            break
    return patches
