from __future__ import annotations

from datetime import datetime, timezone

from patchhive.ops.build_canonical_rig import build_canonical_rig_v1
from patchhive.schemas import (
    JackDirection,
    JackSignalType,
    JackSpec,
    ModuleSection,
    ModuleSpec,
    NormalledEdge,
    Provenance,
    ProvenanceStatus,
    ProvenanceType,
    ResolvedModuleRef,
    RigModuleInput,
    RigSpec,
    ProvenancedValue,
)

FIXED_TIME = datetime(2024, 1, 1, tzinfo=timezone.utc)


def test_vl2_normalled_edges_preserved() -> None:
    module_spec = ModuleSpec(
        module_id="vl2-mode",
        name="VL2 Mode Block",
        manufacturer="VL2",
        width_hp=8,
        sections=[
            ModuleSection(
                section_id="mode",
                label="Mode",
                capability_profile=["normal"],
                jacks=[
                    JackSpec(
                        jack_id="out",
                        label="Out",
                        direction=JackDirection.OUT,
                        signal_type=JackSignalType.CV,
                    )
                ],
                modes=[],
            )
        ],
        normalled_edges=[
            NormalledEdge(from_jack="mode:out", to_jack="mode:in", break_on_insert=True)
        ],
        power_12v_ma=None,
        power_minus12v_ma=None,
        power_5v_ma=None,
    )
    rig_spec = RigSpec(
        rig_id="rig-vl2",
        modules=[
            RigModuleInput(
                module_id=None,
                name=ProvenancedValue(
                    value="VL2 Mode Block",
                    provenance=Provenance(type=ProvenanceType.MANUAL, timestamp=FIXED_TIME),
                    confidence=1.0,
                    status=ProvenanceStatus.CONFIRMED,
                ),
            )
        ],
    )
    resolved = [
        ResolvedModuleRef(
            detection_id="det-1",
            gallery_entry_id="vl2-mode",
            match_confidence=0.95,
            status=ProvenanceStatus.CONFIRMED,
            module_spec=module_spec,
            provenance=Provenance(type=ProvenanceType.GALLERY, timestamp=FIXED_TIME),
        )
    ]

    canonical = build_canonical_rig_v1(rig_spec, resolved)

    assert canonical.normalled_edges
    assert canonical.normalled_edges[0].break_on_insert is True
