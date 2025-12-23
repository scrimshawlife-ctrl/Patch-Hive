from __future__ import annotations

import json
from datetime import datetime, timezone

from patchhive.ops.build_canonical_rig import build_canonical_rig_v1
from patchhive.ops.generate_patch import generate_patch_v1
from patchhive.ops.map_metrics import map_metrics_v1
from patchhive.ops.validate_patch import validate_patch_v1
from patchhive.schemas import (
    CanonicalRig,
    JackDirection,
    JackSignalType,
    JackSpec,
    ModuleSection,
    ModuleSpec,
    NormalledEdge,
    Provenance,
    ProvenancedValue,
    ProvenanceStatus,
    ProvenanceType,
    ResolvedModuleRef,
    RigModuleInput,
    RigSpec,
)

FIXED_TIME = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _dump(model: object) -> str:
    return json.dumps(
        model,  # type: ignore[arg-type]
        sort_keys=True,
        default=lambda o: o.model_dump(mode="json"),
    )


def _build_canonical() -> CanonicalRig:
    module_spec = ModuleSpec(
        module_id="vl2-fg",
        name="VL2 Function Generator",
        manufacturer="VL2",
        width_hp=10,
        sections=[
            ModuleSection(
                section_id="fg",
                label="Function Generator",
                capability_profile=["modulator"],
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
        normalled_edges=[NormalledEdge(from_jack="fg:out", to_jack="fg:in", break_on_insert=True)],
        power_12v_ma=None,
        power_minus12v_ma=None,
        power_5v_ma=None,
    )
    rig_spec = RigSpec(
        rig_id="rig-001",
        modules=[
            RigModuleInput(
                module_id=None,
                name=ProvenancedValue(
                    value="VL2 Function Generator",
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
            gallery_entry_id="vl2-fg",
            match_confidence=0.9,
            status=ProvenanceStatus.CONFIRMED,
            module_spec=module_spec,
            provenance=Provenance(type=ProvenanceType.GALLERY, timestamp=FIXED_TIME),
        )
    ]
    return build_canonical_rig_v1(rig_spec, resolved)


def test_determinism_pipeline() -> None:
    canonical_a = _build_canonical()
    canonical_b = _build_canonical()
    assert _dump(canonical_a) == _dump(canonical_b)

    metrics_a = map_metrics_v1(canonical_a)
    metrics_b = map_metrics_v1(canonical_b)
    assert _dump(metrics_a) == _dump(metrics_b)

    graph_a, plan_a, variations_a = generate_patch_v1(
        rig_id=canonical_a.rig_id,
        intent="Test",
        seed=42,
        module_ids=[module.canonical_id for module in canonical_a.modules],
        normalled_edges=canonical_a.normalled_edges,
    )
    graph_b, plan_b, variations_b = generate_patch_v1(
        rig_id=canonical_b.rig_id,
        intent="Test",
        seed=42,
        module_ids=[module.canonical_id for module in canonical_b.modules],
        normalled_edges=canonical_b.normalled_edges,
    )
    assert _dump(graph_a) == _dump(graph_b)
    assert _dump(plan_a) == _dump(plan_b)
    assert _dump(variations_a) == _dump(variations_b)

    report_a = validate_patch_v1(graph_a)
    report_b = validate_patch_v1(graph_b)
    assert _dump(report_a) == _dump(report_b)
