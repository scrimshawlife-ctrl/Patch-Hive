from __future__ import annotations

from datetime import datetime, timezone

from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    GalleryImageRef,
    JackDir,
    ModuleGalleryEntry,
    ModuleJackEntry,
    PatchIntent,
    Provenance,
    ProvenanceType,
    RigSpec,
    SignalContract,
    SignalKind,
    SignalRate,
)


def _meta_confirmed() -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=datetime(2025, 12, 21, tzinfo=timezone.utc),
                evidence_ref="fixture",
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )


def gallery_voice_entry() -> ModuleGalleryEntry:
    meta = _meta_confirmed()
    signal = SignalContract(kind=SignalKind.audio, rate=SignalRate.audio, meta=meta)
    signal_in = SignalContract(kind=SignalKind.audio, rate=SignalRate.audio, meta=meta)
    return ModuleGalleryEntry(
        module_gallery_id="mod.basic.voice",
        rev=datetime(2025, 12, 21, tzinfo=timezone.utc),
        canonical_name="Basic Voice",
        hp=12,
        images=[GalleryImageRef(url="fixture://basic-voice.png", kind="fixture", meta=meta)],
        jacks=[
            ModuleJackEntry(jack_id="jack.in", label="IN", dir=JackDir.in_, signal=signal_in),
            ModuleJackEntry(jack_id="jack.out", label="OUT", dir=JackDir.out, signal=signal),
        ],
        sketch="fixture",
        meta=meta,
    )


def rigspec_voice_min() -> RigSpec:
    return RigSpec(rig_id="rig.basic.voice", module_gallery_ids=["mod.basic.voice"])
