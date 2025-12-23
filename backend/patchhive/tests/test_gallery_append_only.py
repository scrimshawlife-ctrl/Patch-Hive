from datetime import datetime, timezone, timedelta
from pathlib import Path

from patchhive.gallery.render_sketch import render_module_sketch_svg
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.schemas import ModuleGalleryEntry, JackSpec, ProvenanceRecord


def _entry(rev_time: datetime, name: str = "Maths") -> ModuleGalleryEntry:
    return ModuleGalleryEntry(
        module_gallery_id="mod.make_noise.maths",
        rev=rev_time,
        name=name,
        manufacturer="Make Noise",
        hp=20,
        power=None,
        jacks=[
            JackSpec(
                jack_id="ch1.in",
                label="CH1 IN",
                name="ch1.in",
                signal_type="cv",
                direction="input",
            )
        ],
        modes=None,
        images=[],
        sketch_svg=None,
        provenance=[
            ProvenanceRecord(
                type="manual",
                model_version=None,
                timestamp=rev_time,
                evidence_ref="manual",
            )
        ],
        notes=[],
    )


def test_append_only_gallery(tmp_path: Path) -> None:
    store = ModuleGalleryStore(tmp_path)
    rev1 = datetime(2025, 12, 21, tzinfo=timezone.utc)
    entry = _entry(rev1)
    path = store.append_revision(entry)
    assert path.exists()
    try:
        store.append_revision(entry)
        assert False, "Expected rev collision error"
    except ValueError:
        pass
    latest = store.get_latest("mod.make_noise.maths")
    assert latest is not None
    assert latest.rev == rev1
    rev2 = rev1 + timedelta(seconds=1)
    updated = _entry(rev2, name="Maths (verified name)")
    did_append, path2 = store.ensure_appended_if_changed(updated)
    assert did_append is True
    assert path2 is not None and path2.exists()
    revs = store.list_revisions("mod.make_noise.maths")
    assert len(revs) == 2


def test_sketch_svg_is_deterministic() -> None:
    rev = datetime(2025, 12, 21, tzinfo=timezone.utc)
    entry = _entry(rev)
    first = render_module_sketch_svg(entry)
    second = render_module_sketch_svg(entry)
    assert first == second
    assert "<svg" in first and "circle" in first
