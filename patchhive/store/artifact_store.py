from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


def _stable_id(*parts: str) -> str:
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return h


@dataclass(frozen=True)
class ArtifactRefs:
    run_id: str
    root: Path
    rigspec_path: Path
    library_path: Path
    manifest_path: Path
    summary_path: Path
    pdf_path: Path
    svgs_dir: Path


class ArtifactStore:
    """
    File layout:
      store_root/
        runs/<run_id>/
          rigspec.json
          library.json
          manifest.json
          summary.json
          pdf/patchbook.pdf
          svgs/*.svg
          inputs/input.json           (e2e config + request metadata)
    """

    def __init__(self, store_root: str):
        self.root = Path(store_root)
        (self.root / "runs").mkdir(parents=True, exist_ok=True)

    def alloc_run(self, *, rig_id: str, image_ref: str, preset: str) -> ArtifactRefs:
        run_id = _stable_id(rig_id, image_ref, preset)
        run_root = self.root / "runs" / run_id
        (run_root / "pdf").mkdir(parents=True, exist_ok=True)
        (run_root / "svgs").mkdir(parents=True, exist_ok=True)
        (run_root / "inputs").mkdir(parents=True, exist_ok=True)

        return ArtifactRefs(
            run_id=run_id,
            root=run_root,
            rigspec_path=run_root / "rigspec.json",
            library_path=run_root / "json" / "library.json",
            manifest_path=run_root / "manifest.json",
            summary_path=run_root / "summary.json",
            pdf_path=run_root / "pdf" / "patchbook.pdf",
            svgs_dir=run_root / "svgs",
        )

    def write_input(self, refs: ArtifactRefs, payload: Dict) -> None:
        (refs.root / "inputs" / "input.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def exists(self, refs: ArtifactRefs) -> bool:
        return refs.manifest_path.exists() and refs.pdf_path.exists() and refs.library_path.exists()
