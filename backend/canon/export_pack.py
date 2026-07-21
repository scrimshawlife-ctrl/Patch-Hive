"""Deterministic on-disk export pack for sealed canon patch compilations."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from canon.compiler import PatchCompilation
from canon.contracts import canonical_json, canonical_sha256


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return _sha256_bytes(text.encode("utf-8"))


def export_compilation_pack(
    compilation: PatchCompilation,
    *,
    out_dir: str | Path,
) -> dict[str, Any]:
    """Write sealed graph/plan/validation + manifest with content hashes.

    Layout::

      out_dir/
        patch_graph.json
        patch_plan.json
        validation_report.json
        manifest.json
        svgs/  (optional placeholder index)
    """
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "svgs").mkdir(parents=True, exist_ok=True)

    artifacts = {
        "patch_graph.json": compilation.patch_graph,
        "patch_plan.json": compilation.patch_plan,
        "validation_report.json": compilation.validation_report,
    }
    paths: dict[str, str] = {}
    hashes: dict[str, str] = {}
    for name, obj in artifacts.items():
        text = obj.canonical_json()
        digest = _write_text(root / name, text)
        paths[name] = name
        hashes[name] = digest

    # Deterministic SVG placeholder (no DSP render) — documents cable topology count.
    svg_body = (
        f'<svg xmlns="http://www.w3.org/2000/svg" data-patch="{compilation.patch_graph.artifact_id}">'
        f"<title>Patch topology</title>"
        f'<text x="8" y="20">nodes={len(compilation.patch_graph.nodes)} '
        f"edges={len(compilation.patch_graph.edges)}</text></svg>\n"
    )
    svg_rel = f"svgs/{compilation.patch_graph.artifact_id}.svg"
    hashes[svg_rel] = _write_text(root / svg_rel, svg_body)
    paths["svgs"] = svg_rel

    manifest: dict[str, Any] = {
        "schema_version": "patchhive.export_pack.v1",
        "rig_revision_id": compilation.patch_graph.source_rig_revision_id,
        "source_run_id": compilation.patch_graph.source_run_id,
        "generation_seed": compilation.patch_graph.generation_seed,
        "valid": compilation.validation_report.valid,
        "paths": paths,
        "hashes": hashes,
        "compilation_hash": compilation.canonical_hash_value(),
    }
    # Self-hash after body is fixed (exclude nested self hash).
    body_hash = canonical_sha256({k: v for k, v in manifest.items() if k != "manifest_hash"})
    manifest["manifest_hash"] = body_hash
    hashes["manifest.json"] = _write_text(root / "manifest.json", canonical_json(manifest))
    manifest["hashes"] = hashes
    return manifest
