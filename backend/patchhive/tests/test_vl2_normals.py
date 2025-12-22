from __future__ import annotations

from pathlib import Path

from patchhive.fixtures.vl2_fixture import vl2_gallery_entry_min, vl2_rigspec_min
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig


def test_vl2_normals_and_modes_are_preserved(tmp_path: Path):
    store = ModuleGalleryStore(tmp_path)

    # Append gallery entry
    entry = vl2_gallery_entry_min()
    store.append_revision(entry)

    rig = vl2_rigspec_min()
    canon = build_canonical_rig(rig, gallery_store=store)

    assert canon.rig_id == rig.rig_id
    assert len(canon.modules) == 1

    m = canon.modules[0]
    # Modes preserved
    mode_ids = [mm.mode_id for mm in m.modes]
    assert "fn.lfo" in mode_ids
    assert "fn.env" in mode_ids

    # Normals preserved and explicit
    assert len(canon.normalled_edges) == 1
    e = canon.normalled_edges[0]
    assert e.from_jack == "vl2.internal.clock_out"
    assert e.to_jack == "vl2.seq.clock_in"
    assert e.behavior.value == "break_on_insert"

    # Jack ordering deterministic by jack_id
    jack_ids = [j.jack_id for j in m.jacks]
    assert jack_ids == sorted(jack_ids)
