from __future__ import annotations

from pathlib import Path
from patchhive.export.export_bundle_zip import build_bundle_zip


def test_bundle_zip_builds(tmp_path: Path):
    run_root = tmp_path / "run"
    (run_root / "pdf").mkdir(parents=True)
    (run_root / "json").mkdir(parents=True)
    (run_root / "svgs").mkdir(parents=True)

    # fake artifacts
    (run_root / "rigspec.json").write_text("{}", encoding="utf-8")
    (run_root / "json" / "library.json").write_text("{}", encoding="utf-8")
    (run_root / "manifest.json").write_text("{}", encoding="utf-8")
    (run_root / "summary.json").write_text("{}", encoding="utf-8")
    (run_root / "pdf" / "patchbook.pdf").write_bytes(b"%PDF-FAKE")
    (run_root / "svgs" / "x.svg").write_text("<svg/>", encoding="utf-8")

    out_zip = tmp_path / "out.zip"
    p = build_bundle_zip(str(run_root), str(out_zip))
    assert Path(p).exists()
    assert Path(p).stat().st_size > 0


def test_bundle_zip_partial_artifacts(tmp_path: Path):
    """Test that bundle creation works even if some artifacts are missing."""
    run_root = tmp_path / "run"
    (run_root / "json").mkdir(parents=True)

    # only create a subset of artifacts
    (run_root / "rigspec.json").write_text("{}", encoding="utf-8")
    (run_root / "json" / "library.json").write_text("{}", encoding="utf-8")

    out_zip = tmp_path / "out.zip"
    p = build_bundle_zip(str(run_root), str(out_zip))
    assert Path(p).exists()
    assert Path(p).stat().st_size > 0
