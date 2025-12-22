from __future__ import annotations

from datetime import datetime, timezone

from patchhive.schemas import (
    JackDir,
    ModuleGalleryEntry,
    ModuleJack,
    RigModuleInstance,
    RigSpec,
    RigSource,
    SignalContract,
    SignalKind,
    SignalRate,
)


def vl2_gallery_entry_min() -> ModuleGalleryEntry:
    return ModuleGalleryEntry(
        module_gallery_id="vl2-clock",
        rev=datetime(2025, 1, 1, tzinfo=timezone.utc),
        name="VL2 Clock",
        manufacturer="PatchHive",
        hp=8,
        tags=["clock", "semi-normalled"],
        jacks=[
            ModuleJack(
                jack_id="clock.in",
                label="Clock In",
                dir=JackDir.in_,
                signal=SignalContract(
                    kind=SignalKind.clock,
                    rate=SignalRate.control,
                    range_v=None,
                    polarity="unknown",
                    meta=None,
                ),
                meta=None,
            ),
            ModuleJack(
                jack_id="gate.out",
                label="Gate Out",
                dir=JackDir.out,
                signal=SignalContract(
                    kind=SignalKind.gate,
                    rate=SignalRate.control,
                    range_v=None,
                    polarity="unknown",
                    meta=None,
                ),
                meta=None,
            ),
        ],
        modes=["main"],
        images=[],
        sketch_svg=None,
        provenance=[],
        notes=[],
    )


def vl2_rigspec_min() -> RigSpec:
    return RigSpec(
        rig_id="rig-vl2-min",
        name="VL2 Minimal",
        source=RigSource.manual_picklist,
        modules=[
            RigModuleInstance(
                instance_id="vl2-1",
                gallery_module_id="vl2-clock",
                gallery_rev=None,
                observed_placement=None,
                meta=None,
            )
        ],
        normalled_edges=[],
        provenance=[],
        notes=[],
    )
