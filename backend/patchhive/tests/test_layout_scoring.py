from __future__ import annotations

import json
from datetime import datetime, timezone

from patchhive.ops.suggest_layouts import suggest_layouts_v1
from patchhive.schemas import (
    CanonicalModule,
    CanonicalRig,
    ModuleSection,
    ModuleSpec,
    Provenance,
    ProvenanceStatus,
    ProvenanceType,
)

FIXED_TIME = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _dump(model: object) -> str:
    return json.dumps(
        model,  # type: ignore[arg-type]
        sort_keys=True,
        default=lambda o: o.model_dump(mode="json"),
    )


def test_layout_scoring_deterministic() -> None:
    module_spec = ModuleSpec(
        module_id="vl2-filter",
        name="VL2 Filter",
        manufacturer="VL2",
        width_hp=8,
        sections=[ModuleSection(section_id="flt", label="Filter", capability_profile=[], jacks=[])],
        normalled_edges=[],
        power_12v_ma=None,
        power_minus12v_ma=None,
        power_5v_ma=None,
    )
    canonical = CanonicalRig(
        rig_id="rig-layout",
        modules=[
            CanonicalModule(
                canonical_id="vl2-filter-01",
                module_spec=module_spec,
                provenance=Provenance(type=ProvenanceType.GALLERY, timestamp=FIXED_TIME),
                confidence=0.9,
                status=ProvenanceStatus.CONFIRMED,
                observed_position=None,
            )
        ],
        normalled_edges=[],
    )

    layouts_a = suggest_layouts_v1(canonical, user_profile="user", seed=7)
    layouts_b = suggest_layouts_v1(canonical, user_profile="user", seed=7)

    assert _dump(layouts_a) == _dump(layouts_b)
    assert len(layouts_a) == 3
    assert all("reach_cost" in layout.breakdown for layout in layouts_a)
