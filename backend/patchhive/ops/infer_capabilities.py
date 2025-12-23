from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Set

from patchhive.schemas import CanonicalRig, JackDir, SignalKind


@dataclass(frozen=True)
class ModuleCaps:
    instance_id: str
    caps: Set[str]


def infer_capabilities(canon: CanonicalRig) -> Dict[str, ModuleCaps]:
    """
    Deterministic, conservative capability inference from jack kinds + direction.
    Later: incorporate function_id registry + manufacturer hints.
    """
    out: Dict[str, ModuleCaps] = {}

    for module in sorted(canon.modules, key=lambda x: x.instance_id):
        kinds_out: Set[SignalKind] = set()
        kinds_in: Set[SignalKind] = set()
        n_in = 0
        n_out = 0

        for jack in module.jacks:
            if jack.dir in (JackDir.out, JackDir.bidir):
                n_out += 1
                kinds_out.add(jack.signal.kind)
            if jack.dir in (JackDir.in_, JackDir.bidir):
                n_in += 1
                kinds_in.add(jack.signal.kind)

        caps: Set[str] = set()

        # audio chain hints
        if SignalKind.audio in kinds_out and SignalKind.audio in kinds_in:
            caps.add("fx_or_processor")
        if SignalKind.audio in kinds_out and (
            SignalKind.cv in kinds_in or SignalKind.cv_or_audio in kinds_in
        ):
            caps.add("vca_or_filter_or_wavefolder")

        # modulation sources
        if any(
            kind in kinds_out
            for kind in (SignalKind.lfo, SignalKind.envelope, SignalKind.random, SignalKind.cv)
        ):
            caps.add("mod_source")

        # clocking
        if SignalKind.clock in kinds_out:
            caps.add("clock_source")
        if SignalKind.clock in kinds_in:
            caps.add("clock_sink")

        # sequencer-ish: clock in + pitch/gate out
        if SignalKind.clock in kinds_in and any(
            kind in kinds_out for kind in (SignalKind.gate, SignalKind.trigger, SignalKind.pitch_cv)
        ):
            caps.add("sequencer_like")

        # utility: many ins or outs can imply mixing/multing
        if n_in >= 3 and SignalKind.audio in kinds_in and SignalKind.audio in kinds_out:
            caps.add("audio_mixer_like")
        if n_out >= 3 and SignalKind.cv in kinds_out:
            caps.add("cv_mult_like")

        out[module.instance_id] = ModuleCaps(instance_id=module.instance_id, caps=caps)

    return out
