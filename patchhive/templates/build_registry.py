from __future__ import annotations

from patchhive.templates.registry import build_default_registry, PatchTemplateRegistry
from patchhive.templates.vl2_pack_v1 import register_vl2_pack_v1
from patchhive.templates.vl2_micro_grammar import register_vl2_micro_grammar
from patchhive.ops.detect_signatures import detect_signatures
from patchhive.schemas import CanonicalRig


def build_registry_for_rig(canon: CanonicalRig) -> PatchTemplateRegistry:
    """
    Build a patch template registry tailored to the given rig.
    Activates specialized template sets based on detected signature modules.
    """
    reg = build_default_registry()
    reg = register_vl2_pack_v1(reg)

    sig = detect_signatures(canon)
    if sig.get("has_vl2"):
        reg = register_vl2_micro_grammar(reg)

    return reg
