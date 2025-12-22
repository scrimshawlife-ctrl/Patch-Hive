from __future__ import annotations

from pathlib import Path

from patchhive.fixtures.vl2_fixture import vl2_gallery_entry_min, vl2_rigspec_min
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.map_metrics import map_metrics
from patchhive.ops.suggest_layouts import CaseSpec, suggest_layouts


def test_layouts_are_deterministic(tmp_path: Path):
    store = ModuleGalleryStore(tmp_path)
    store.append_revision(vl2_gallery_entry_min())

    rig = vl2_rigspec_min()
    canon = build_canonical_rig(rig, gallery_store=store)
    metrics = map_metrics(canon)

    layouts1 = suggest_layouts(canon, metrics, case=CaseSpec(rows=1, row_hp=104))
    layouts2 = suggest_layouts(canon, metrics, case=CaseSpec(rows=1, row_hp=104))

    assert [l.to_canonical_json() for l in layouts1] == [l.to_canonical_json() for l in layouts2]
    assert len(layouts1) == 3
    assert {l.layout_type.value for l in layouts1} == {"Beginner", "Performance", "Experimental"}


def test_layouts_include_placements(tmp_path: Path):
    store = ModuleGalleryStore(tmp_path)
    store.append_revision(vl2_gallery_entry_min())

    rig = vl2_rigspec_min()
    canon = build_canonical_rig(rig, gallery_store=store)
    metrics = map_metrics(canon)

    layouts = suggest_layouts(canon, metrics, case=CaseSpec(rows=1, row_hp=104))
    for l in layouts:
        assert len(l.placements) == len(canon.modules)
        # placements must be within case bounds
        for p in l.placements:
            assert 0 <= p.row < 1
            assert 0 <= p.x_hp < 104
