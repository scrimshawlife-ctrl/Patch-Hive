from __future__ import annotations

from datetime import datetime, timezone

from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    JackDir,
    ModuleGalleryEntry,
    ModuleJack,
    ModuleMode,
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


def _meta_confirmed(evidence_ref: str) -> FieldMeta:
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


def vl2_gallery_entry_min(rev: datetime | None = None) -> ModuleGalleryEntry:
    """
    A minimal 'VL2 core' style entry with:
    - a clock out
    - a sequencer clock in
    - a function gen with modes (LFO vs ENV)
    """
    rev = rev or datetime(2025, 12, 21, 12, 0, 0, tzinfo=timezone.utc)
    m = _meta_confirmed("fixture:vl2:gallery")

    j_clock_out = ModuleJack(
        jack_id="vl2.internal.clock_out",
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
    j_seq_clk_in = ModuleJack(
        jack_id="vl2.seq.clock_in",
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
    j_fn_out = ModuleJack(
        jack_id="vl2.fn.out",
        label="FN OUT",
        dir=JackDir.out,
        signal=SignalContract(
            kind=SignalKind.cv,
            rate=SignalRate.control,
            range_v=(0.0, 8.0),
            polarity="unipolar",
            meta=None,
        ),
        meta=m,
    )

    mode_lfo = ModuleMode(
        mode_id="fn.lfo",
        label="Function: LFO",
        jack_overrides=None,
        tags=["lfo", "modulator"],
        meta=m,
    )
    mode_env = ModuleMode(
        mode_id="fn.env",
        label="Function: Envelope",
        jack_overrides=None,
        tags=["envelope", "controller"],
        meta=m,
    )

    return ModuleGalleryEntry(
        module_gallery_id="mod.erica.vl2.core",
        rev=rev,
        name="Voltage Lab 2 Core (Minimal)",
        manufacturer="Erica Synths",
        hp=104,
        tags=["semi-normalled", "west-coast", "sequencing"],
        power=PowerSpec(plus12_ma=None, minus12_ma=None, plus5_ma=None, meta=m),
        jacks=[j_clock_out, j_seq_clk_in, j_fn_out],
        modes=[mode_lfo, mode_env],
        images=[],
        sketch_svg=None,
        provenance=[],
        notes=["Fixture: minimal VL2 core representation"],
    )


def vl2_rigspec_min() -> RigSpec:
    """
    RigSpec includes explicit semi-normalled route:
      internal clock_out -> seq clock_in (break_on_insert)
    """
    m = _meta_confirmed("fixture:vl2:rigspec")

    inst = RigModuleInstance(
        instance_id="inst.vl2.core.1",
        gallery_module_id="mod.erica.vl2.core",
        gallery_rev=None,  # allow latest
        observed_placement=None,
        meta=m,
    )

    edge = NormalledEdge(
        from_jack="vl2.internal.clock_out",
        to_jack="vl2.seq.clock_in",
        behavior=NormalledBehavior.break_on_insert,
        meta=m,
    )

    return RigSpec(
        rig_id="rig.vl2.fixture.v1",
        name="VL2 Fixture Rig",
        source=RigSource.manual_picklist,
        modules=[inst],
        normalled_edges=[edge],
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=datetime(2025, 12, 21, 0, 0, 0, tzinfo=timezone.utc),
                evidence_ref="fixture:vl2",
            )
        ],
        notes=[],
    )
