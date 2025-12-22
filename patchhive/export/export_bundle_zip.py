from __future__ import annotations

import zipfile
from pathlib import Path
from typing import List


def build_bundle_zip(run_root: str, out_zip: str) -> str:
    """
    Bundles:
      rigspec.json
      library.json
      manifest.json
      summary.json
      pdf/patchbook.pdf
      svgs/*.svg
    """
    root = Path(run_root)
    outp = Path(out_zip)
    outp.parent.mkdir(parents=True, exist_ok=True)

    include = [
        root / "rigspec.json",
        root / "json" / "library.json",
        root / "manifest.json",
        root / "summary.json",
        root / "pdf" / "patchbook.pdf",
    ]
    svg_dir = root / "svgs"
    svgs = list(svg_dir.glob("*.svg")) if svg_dir.exists() else []
    include.extend(svgs)

    with zipfile.ZipFile(outp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in include:
            if not p.exists():
                continue
            z.write(p, arcname=str(p.relative_to(root)))

    return str(outp)
