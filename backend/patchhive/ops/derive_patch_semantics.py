"""Structure-aware naming helpers for PatchHive."""
from collections import Counter
from hashlib import sha256
from typing import Dict

from patchhive.schemas import CanonicalRig, PatchGraph, SignalKind


def derive_patch_semantics(
    canon: CanonicalRig,
    patch: PatchGraph,
) -> Dict[str, str]:
    """
    Deterministic semantic compression of a patch's signal flow.
    """
    kinds_out = []
    kinds_in = []

    for c in patch.cables:
        from_id = getattr(c.from_jack, "jack_id", c.from_jack)
        to_id = getattr(c.to_jack, "jack_id", c.to_jack)

        for m in canon.modules:
            for j in m.jacks:
                if j.jack_id == from_id:
                    kinds_out.append(j.signal.kind)
                if j.jack_id == to_id:
                    kinds_in.append(j.signal.kind)

    outc = Counter(kinds_out)
    inc = Counter(kinds_in)

    source = (
        "Voice" if outc[SignalKind.audio]
        else "Random" if outc[SignalKind.random]
        else "LFO" if outc[SignalKind.lfo]
        else "Clock" if outc[SignalKind.clock]
        else "Source"
    )

    transform = (
        "Shaped" if inc[SignalKind.audio] and inc[SignalKind.cv]
        else "Filtered" if inc[SignalKind.audio]
        else "Modulated" if inc[SignalKind.cv]
        else "Path"
    )

    control = (
        "Enveloped" if outc[SignalKind.envelope]
        else "Cycled" if outc[SignalKind.lfo]
        else "Drifting" if outc[SignalKind.random]
        else "Free"
    )

    clocked = "Clocked" if (outc[SignalKind.clock] or inc[SignalKind.clock]) else "Free"

    return {
        "source": source,
        "transform": transform,
        "control": control,
        "clocked": clocked,
    }


def name_patch_v2(
    canon: CanonicalRig,
    patch: PatchGraph,
) -> str:
    """
    Stable, structure-derived patch name.
    """
    sem = derive_patch_semantics(canon, patch)
    mk = sha256(patch.patch_id.encode()).hexdigest()[:4].upper()
    return f"{sem['source']} {sem['control']} {sem['transform']} Mk.{mk}"
