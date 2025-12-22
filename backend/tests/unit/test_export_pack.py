from __future__ import annotations

from pathlib import Path

from patchhive.export.export_pack import export_pack
from patchhive.fixtures.basic_voice_fixture import gallery_voice_entry, rigspec_voice_min
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.pipeline.run_library import run_library
from patchhive.schemas_library import PatchSpaceConstraints


def test_export_pack_writes_files(tmp_path: Path) -> None:
    gallery_root = tmp_path / "gallery"
    out_dir = tmp_path / "out"
    store = ModuleGalleryStore(gallery_root)
    store.append_revision(gallery_voice_entry())

    rig = rigspec_voice_min()
    canon = build_canonical_rig(rig, gallery_store=store)

    library = run_library(
        canon,
        constraints=PatchSpaceConstraints(max_cables=4),
        include_diagrams=False,
    )
    manifest = export_pack(canon, library, out_dir=str(out_dir))

    assert (out_dir / "library.json").exists()
    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "pdf" / "patchbook.pdf").exists()
    assert (out_dir / "svgs").exists()
    assert any(p.suffix == ".svg" for p in (out_dir / "svgs").iterdir())
    assert "hashes" in manifest and manifest["hashes"]
