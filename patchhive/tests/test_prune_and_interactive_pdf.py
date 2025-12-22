from __future__ import annotations

from pathlib import Path

from patchhive.fixtures.basic_voice_fixture import gallery_voice_entry, rigspec_voice_min
from patchhive.gallery.store import ModuleGalleryStore
from patchhive.ops.build_canonical_rig import build_canonical_rig
from patchhive.pipeline.run_library import run_library
from patchhive.presets.library_presets import core_preset
from patchhive.ops.prune_library import prune_library, LibraryPruneSpec
from patchhive.export.export_library_pdf_interactive import export_library_pdf_interactive


def test_prune_and_pdf(tmp_path: Path) -> None:
    store = ModuleGalleryStore(tmp_path / "gallery")
    store.append_revision(gallery_voice_entry())

    rig = rigspec_voice_min()
    canon = build_canonical_rig(rig, gallery_store=store)

    lib = run_library(canon, constraints=core_preset(), include_diagrams=False)
    lib2 = prune_library(lib, LibraryPruneSpec(max_total=10, max_per_category=10, drop_runaway=True))

    assert len(lib2.patches) <= 10

    out_pdf = tmp_path / "patchbook.pdf"
    export_library_pdf_interactive(canon, lib2, out_pdf=str(out_pdf))

    assert out_pdf.exists()
