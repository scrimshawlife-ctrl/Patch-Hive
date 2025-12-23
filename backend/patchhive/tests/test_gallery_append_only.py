from __future__ import annotations

from datetime import datetime, timezone

from patchhive.gallery.store import ModuleGalleryStore
from patchhive.schemas import (
    ModuleGalleryEntry,
    ModuleSection,
    ModuleSpec,
    NormalledEdge,
    Provenance,
    ProvenanceType,
)

FIXED_TIME = datetime(2024, 1, 1, tzinfo=timezone.utc)


def test_gallery_append_only(tmp_path) -> None:
    path = tmp_path / "gallery.jsonl"
    store = ModuleGalleryStore(path)

    base_spec = ModuleSpec(
        module_id="vl2-osc",
        name="VL2 Osc",
        manufacturer="VL2",
        width_hp=6,
        sections=[ModuleSection(section_id="osc", label="Osc", capability_profile=[], jacks=[])],
        normalled_edges=[
            NormalledEdge(from_jack="osc:out", to_jack="osc:in", break_on_insert=True)
        ],
        power_12v_ma=None,
        power_minus12v_ma=None,
        power_5v_ma=None,
    )
    entry_v1 = ModuleGalleryEntry(
        entry_id="vl2-osc",
        revision_id="vl2-osc-rev1",
        previous_revision_id=None,
        created_at=FIXED_TIME,
        name="VL2 Osc",
        manufacturer="VL2",
        spec=base_spec,
        provenance=Provenance(type=ProvenanceType.MANUAL, timestamp=FIXED_TIME),
    )
    entry_v2 = ModuleGalleryEntry(
        entry_id="vl2-osc",
        revision_id="vl2-osc-rev2",
        previous_revision_id="vl2-osc-rev1",
        created_at=FIXED_TIME,
        name="VL2 Osc",
        manufacturer="VL2",
        spec=base_spec,
        provenance=Provenance(type=ProvenanceType.DERIVED, timestamp=FIXED_TIME),
    )

    store.append(entry_v1)
    store.append(entry_v2)

    history = store.history("vl2-osc")
    assert len(history) == 2
    assert history[0].revision_id == "vl2-osc-rev1"
    assert history[1].revision_id == "vl2-osc-rev2"
