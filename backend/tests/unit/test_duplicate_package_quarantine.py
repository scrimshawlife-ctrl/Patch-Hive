from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _run_import(module: str, *, extra_path: Path | None = None, allow: bool = False) -> subprocess.CompletedProcess[str]:
    python_path = str(extra_path or ROOT)
    env = {
        **os.environ,
        "PYTHONPATH": python_path,
        "PATCHHIVE_ENV": "production",
    }
    if allow:
        env["PATCHHIVE_ALLOW_LEGACY_IMPORTS"] = "1"
    else:
        env.pop("PATCHHIVE_ALLOW_LEGACY_IMPORTS", None)
    return subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_top_level_patchhive_is_blocked_in_production_like_runtime() -> None:
    result = _run_import("patchhive")

    assert result.returncode != 0
    assert "Refusing to import legacy top-level patchhive package" in result.stderr


def test_top_level_patchhive_allows_explicit_compatibility_job() -> None:
    result = _run_import("patchhive", allow=True)

    assert result.returncode == 0, result.stderr


def test_patch_hive_is_blocked_in_production_like_runtime() -> None:
    result = _run_import("patch_hive", extra_path=ROOT / "patch_hive")

    assert result.returncode != 0
    assert "Refusing to import legacy patch_hive package" in result.stderr


def test_overlay_is_blocked_in_production_like_runtime() -> None:
    result = _run_import("patchhive_overlay")

    assert result.returncode != 0
    assert "Refusing to import legacy patchhive_overlay package" in result.stderr
