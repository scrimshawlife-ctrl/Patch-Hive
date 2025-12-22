from __future__ import annotations

from datetime import datetime, timezone

from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    JackDir,
    ModuleGalleryEntry,
    ModuleJack,
    NormalledBehavior,
    NormalledEdge,
    PowerSpec,
    Provenance,
    ProvenanceType,
    RigModuleInstance,
    RigSource,
    RigSpec,
    SignalContract,
    SignalKind,
    SignalRate,
)


def _meta(evidence_ref: str) -> FieldMeta:
    return FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=datetime(2025, 12, 21, 0, 0, 0, tzinfo=timezone.utc),
                evidence_ref=evidence_ref,
            )
        ],
        confidence=1.0,
        status=FieldStatus.confirmed,
    )


def gallery_voice_entry(rev: datetime | None = None) -> ModuleGalleryEntry:
    rev = rev or datetime(2025, 12, 21, 12, 0, 0, tzinfo=timezone.utc)
    m = _meta("fixture:voice:gallery")

    osc_out = ModuleJack(
        jack_id="osc.audio_out",
        label="OSC OUT",
        dir=JackDir.out,
        signal=SignalContract(
            kind=SignalKind.audio,
            rate=SignalRate.audio,
            range_v=None,
            polarity="unknown",
            meta=None,
        ),
        meta=m,
    )
    vca_in = ModuleJack(
        jack_id="vca.audio_in",
        label="VCA IN",
        dir=JackDir.in_,
        signal=SignalContract(
            kind=SignalKind.audio,
            rate=SignalRate.audio,
            range_v=None,
            polarity="unknown",
            meta=None,
        ),
        meta=m,
    )
    out_in = ModuleJack(
        jack_id="out.audio_in",
        label="OUT IN",
        dir=JackDir.in_,
        signal=SignalContract(
            kind=SignalKind.audio,
            rate=SignalRate.audio,
            range_v=None,
            polarity="unknown",
            meta=None,
        ),
        meta=m,
    )
    lfo_out = ModuleJack(
        jack_id="lfo.cv_out",
        label="LFO OUT",
        dir=JackDir.out,
        signal=SignalContract(
            kind=SignalKind.lfo,
            rate=SignalRate.control,
            range_v=None,
            polarity="unknown",
            meta=None,
        ),
        meta=m,
    )
    cv_in = ModuleJack(
        jack_id="vca.cv_in",
        label="VCA CV",
        dir=JackDir.in_,
        signal=SignalContract(
            kind=SignalKind.cv,
            rate=SignalRate.control,
            range_v=None,
            polarity="unknown",
            meta=None,
        ),
        meta=m,
    )
    clk_out = ModuleJack(
        jack_id="clk.clock_out",
        label="CLK OUT",
        dir=JackDir.out,
        signal=SignalContract(
            kind=SignalKind.clock,
            rate=SignalRate.control,
            range_v=(0.0, 5.0),
            polarity="unipolar",
            meta=None,
        ),
        meta=m,
    )
    clk_in = ModuleJack(
        jack_id="seq.clock_in",
        label="SEQ CLK IN",
        dir=JackDir.in_,
        signal=SignalContract(
            kind=SignalKind.clock,
            rate=SignalRate.control,
            range_v=(0.0, 5.0),
            polarity="unipolar",
            meta=None,
        ),
        meta=m,
    )

    return ModuleGalleryEntry(
        module_gallery_id="mod.fixture.voice.v1",
        rev=rev,
        name="Fixture Voice Rig Module Set",
        manufacturer="PatchHive",
        hp=42,
        tags=["oscillator", "vca", "lfo", "clock", "sequencer", "output"],
        power=PowerSpec(plus12_ma=None, minus12_ma=None, plus5_ma=None, meta=m),
        jacks=[osc_out, vca_in, out_in, lfo_out, cv_in, clk_out, clk_in],
        modes=[],
        images=[],
        sketch_svg=None,
        provenance=[],
        notes=["Fixture module with multiple jack kinds for generator tests."],
    )


def rigspec_voice_min() -> RigSpec:
    m = _meta("fixture:voice:rigspec")

    inst = RigModuleInstance(
        instance_id="inst.fixture.voice.1",
        gallery_module_id="mod.fixture.voice.v1",
        gallery_rev=None,
        observed_placement=None,
        meta=m,
    )

    # Semi-normalled example: osc_out normalled to vca_in
    edge = NormalledEdge(
        from_jack="osc.audio_out",
        to_jack="vca.audio_in",
        behavior=NormalledBehavior.break_on_insert,
        meta=m,
    )

    return RigSpec(
        rig_id="rig.fixture.voice.v1",
        name="Fixture Voice Rig",
        source=RigSource.manual_picklist,
        modules=[inst],
        normalled_edges=[edge],
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=datetime(2025, 12, 21, 0, 0, 0, tzinfo=timezone.utc),
                evidence_ref="fixture:voice",
            )
        ],
        notes=[],
    )
