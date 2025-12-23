from __future__ import annotations

from patchhive.ops.generate_patch_candidates import build_patch_library
from patchhive.schemas import CanonicalRig
from patchhive.templates.registry import build_default_registry
from patchhive.templates.vl2_pack_v1 import register_vl2_pack_v1


def run_library(canon: CanonicalRig) -> dict[str, list[dict[str, str]]]:
    reg = build_default_registry()
    reg = register_vl2_pack_v1(reg)
    return build_patch_library(canon, reg)
