from datetime import datetime, timezone

from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.suggest_layouts import suggest_layouts
from patchhive.schemas import ModuleGalleryEntry, JackSpec, ProvenanceRecord


def _entry(module_id: str, name: str, hp: int) -> ModuleGalleryEntry:
    timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return ModuleGalleryEntry(
        module_gallery_id=module_id,
        rev=timestamp,
        name=name,
        manufacturer="AAL",
        hp=hp,
        power=None,
        jacks=[JackSpec(jack_id="out", label="OUT", name="out", signal_type="audio", direction="output")],
        modes=None,
        images=[],
        sketch_svg=None,
        provenance=[
            ProvenanceRecord(
                type="manual",
                model_version=None,
                timestamp=timestamp,
                evidence_ref="layout",
            )
        ],
        notes=[],
    )


def test_layout_scoring() -> None:
    modules = [
        _entry("mod-1", "Osc", 10),
        _entry("mod-2", "Filter", 8),
        _entry("mod-3", "Mixer", 6),
    ]
    rig = build_canonical_rig("rig-layout", modules)
    layouts = suggest_layouts(rig, row_hp=20)
    assert [layout.layout_type for layout in layouts] == [
        "Beginner",
        "Performance",
        "Experimental",
    ]
    totals = [layout.total_score for layout in layouts]
    assert all(total > 0 for total in totals)
    assert totals[0] == layouts[0].total_score
