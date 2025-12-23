from __future__ import annotations

from itertools import product
from typing import Dict, Iterable, List, Mapping, Sequence

from patchhive.ops.infer_capabilities import ModuleCaps, infer_capabilities
from patchhive.schemas import CanonicalRig, Jack, JackDir, SignalKind
from patchhive.templates.registry import PatchTemplate, PatchTemplateRegistry


def _jack_matches_constraint(constraint: str, jack: Jack) -> bool:
    is_out = jack.dir in (JackDir.out, JackDir.bidir)
    is_in = jack.dir in (JackDir.in_, JackDir.bidir)
    kind = jack.signal.kind

    if constraint == "audio_out":
        return is_out and kind in (SignalKind.audio, SignalKind.cv_or_audio)
    if constraint == "audio_in_or_cv_or_audio_in":
        return is_in and kind in (SignalKind.audio, SignalKind.cv, SignalKind.cv_or_audio)
    if constraint == "cv_out":
        return is_out and kind in (
            SignalKind.cv,
            SignalKind.cv_or_audio,
            SignalKind.lfo,
            SignalKind.envelope,
            SignalKind.random,
            SignalKind.pitch_cv,
            SignalKind.gate,
            SignalKind.trigger,
        )
    if constraint == "gate_out":
        return is_out and kind in (SignalKind.gate, SignalKind.trigger)
    if constraint == "trigger_out":
        return is_out and kind == SignalKind.trigger
    if constraint == "cv_in_or_cv_or_audio_in":
        return is_in and kind in (
            SignalKind.cv,
            SignalKind.cv_or_audio,
            SignalKind.audio,
            SignalKind.lfo,
            SignalKind.envelope,
            SignalKind.random,
            SignalKind.pitch_cv,
            SignalKind.gate,
            SignalKind.trigger,
        )
    if constraint == "clock_out":
        return is_out and kind == SignalKind.clock
    if constraint == "clock_in":
        return is_in and kind == SignalKind.clock

    return False


def _role_satisfies_caps(
    role: str,
    jack_id: str,
    required_caps: Mapping[str, Sequence[str]] | None,
    canon: CanonicalRig,
    caps_map: Mapping[str, ModuleCaps],
) -> bool:
    if not required_caps or role not in required_caps:
        return True
    for module in canon.modules:
        for jack in module.jacks:
            if jack.jack_id == jack_id:
                have = caps_map[module.instance_id].caps
                need_any = set(required_caps[role])
                return bool(have.intersection(need_any))
    return False


def _enumerate_assignments(
    template: PatchTemplate,
    role_to_jacks: Mapping[str, Sequence[str]],
    canon: CanonicalRig,
    caps_map: Mapping[str, object],
) -> List[Dict[str, str]]:
    roles = sorted(role_to_jacks.keys())
    candidates: List[Dict[str, str]] = []
    jack_lists = [role_to_jacks[role] for role in roles]

    for assignment in product(*jack_lists):
        if len(set(assignment)) != len(assignment):
            continue
        mapping = dict(zip(roles, assignment))
        if all(
            _role_satisfies_caps(
                role,
                jack_id,
                template.required_caps,
                canon,
                caps_map,
            )
            for role, jack_id in mapping.items()
        ):
            candidates.append(mapping)

    return candidates


def build_patch_library(
    canon: CanonicalRig, registry: PatchTemplateRegistry
) -> Dict[str, List[Dict[str, str]]]:
    caps_map = infer_capabilities(canon)
    library: Dict[str, List[Dict[str, str]]] = {}

    for template in registry.templates():
        role_to_jacks: Dict[str, List[str]] = {}
        for role, constraints in template.role_constraints.items():
            matches: List[str] = []
            for module in canon.modules:
                for jack in module.jacks:
                    if any(
                        _jack_matches_constraint(constraint, jack) for constraint in constraints
                    ):
                        matches.append(jack.jack_id)
            role_to_jacks[role] = matches

        if role_to_jacks:
            library[template.template_id] = _enumerate_assignments(
                template, role_to_jacks, canon, caps_map
            )

    return library
