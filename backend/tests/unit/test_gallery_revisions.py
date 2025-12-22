from __future__ import annotations

from pathlib import Path

from patchhive.gallery.revisions import GalleryRevision, append_revision


def test_gallery_revisions_append_only(tmp_path: Path) -> None:
    payload_a = {"name": "Module A", "hp": 10}
    payload_b = {"name": "Module A", "hp": 12}

    rev_a = GalleryRevision(module_key="gallery.test.module_a", payload=payload_a)
    rev_b = GalleryRevision(module_key="gallery.test.module_a", payload=payload_b)

    append_revision(str(tmp_path), rev_a, evidence_ref="test:a")
    append_revision(str(tmp_path), rev_b, evidence_ref="test:b")

    revisions_dir = tmp_path / "modules" / "gallery.test.module_a" / "revisions"
    files = sorted(p.name for p in revisions_dir.glob("*.json"))

    assert rev_a.version == 0
    assert rev_b.version == 1
    assert len(files) == 2
