from __future__ import annotations

import re
from datetime import datetime, timezone

from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    JackFunctionEntry,
    Provenance,
    ProvenanceType,
    SignalKind,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s\-_]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _guess_kind(label: str) -> SignalKind:
    l = _norm(label)
    if "clk" in l or "clock" in l:
        return SignalKind.clock
    if "gate" in l:
        return SignalKind.gate
    if "trig" in l:
        return SignalKind.trigger
    if "out" in l and ("audio" in l or "sig" in l):
        return SignalKind.audio
    if any(k in l for k in ["cv", "mod", "fm", "amt", "depth", "fold", "shape", "chaos"]):
        return SignalKind.cv
    return SignalKind.unknown


def propose_function_from_jack_label(
    *,
    manufacturer: str,
    module_name: str,
    jack_label: str,
    evidence_ref: str,
) -> JackFunctionEntry:
    """
    Deterministically propose a new function entry for proprietary labels.
    This is NOT auto-truth. It's a candidate for append-only registry.
    """
    m = _norm(manufacturer).replace(" ", "_")
    mn = _norm(module_name).replace(" ", "_")
    jl = _norm(jack_label).replace(" ", "_")

    function_id = f"fn.{m}.{mn}.{jl}"

    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=_now_utc(),
                evidence_ref=evidence_ref,
                method="function_detect.v1",
            )
        ],
        confidence=0.65,
        status=FieldStatus.inferred,
    )

    return JackFunctionEntry(
        function_id=function_id,
        rev=_now_utc(),
        canonical_name=jack_label.strip(),
        description=(
            "Proposed function derived from proprietary jack label "
            f"'{jack_label}'. Needs confirmation."
        ),
        label_aliases=[jack_label.strip()],
        kind_hint=_guess_kind(jack_label),
        provenance=list(meta.provenance),
        meta=meta,
    )
