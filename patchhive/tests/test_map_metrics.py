from __future__ import annotations

from pathlib import Path

from patchhive.fixtures.vl2_fixture import vl2_gallery_entry_min, vl2_rigspec_min
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.ops.map_metrics import map_metrics
from patchhive.schemas import CapabilityCategory


def test_map_metrics_is_deterministic(tmp_path: Path):
    store = ModuleGalleryStore(tmp_path)
    store.append_revision(vl2_gallery_entry_min())

    rig = vl2_rigspec_min()
    canon = build_canonical_rig(rig, gallery_store=store)

    m1 = map_metrics(canon)
    m2 = map_metrics(canon)

    assert m1.to_canonical_json() == m2.to_canonical_json()


def test_vl2_fixture_has_clock_domain_category(tmp_path: Path):
    store = ModuleGalleryStore(tmp_path)
    store.append_revision(vl2_gallery_entry_min())

    rig = vl2_rigspec_min()
    canon = build_canonical_rig(rig, gallery_store=store)

    pkt = map_metrics(canon)

    # Since the fixture has clock jacks + tags include semi-normalled, we should see Clock Domain and/or Normals.
    assert pkt.category_counts.get(CapabilityCategory.clock_domain, 0) >= 1
