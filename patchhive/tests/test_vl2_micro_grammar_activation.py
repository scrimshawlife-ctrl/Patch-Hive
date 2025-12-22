from __future__ import annotations

from patchhive.ops.detect_signatures import detect_signatures
from patchhive.templates.build_registry import build_registry_for_rig
from patchhive.schemas import CanonicalRig, CanonicalModule


def test_vl2_detection():
    """Test that VL2 signature is detected correctly."""
    # Create a canonical rig with VL2
    canon_vl2 = CanonicalRig(
        rig_id="rig.vl2.test",
        modules=[
            CanonicalModule(
                instance_id="inst.01",
                name="Voltage Lab 2",
                hp=104,
                tags=["module"],
                modes=[],
                jacks=[],
            )
        ],
    )

    sig = detect_signatures(canon_vl2)
    assert sig["has_vl2"] is True


def test_non_vl2_detection():
    """Test that non-VL2 rigs are not flagged as VL2."""
    canon_generic = CanonicalRig(
        rig_id="rig.generic.test",
        modules=[
            CanonicalModule(
                instance_id="inst.01",
                name="Generic Oscillator",
                hp=8,
                tags=[],
                modes=[],
                jacks=[],
            )
        ],
    )

    sig = detect_signatures(canon_generic)
    assert sig["has_vl2"] is False


def test_vl2_registry_activation():
    """Test that VL2 micro-grammar templates are activated when VL2 is detected."""
    canon_vl2 = CanonicalRig(
        rig_id="rig.vl2.test",
        modules=[
            CanonicalModule(
                instance_id="inst.01",
                name="Voltage Lab 2",
                hp=104,
                tags=[],
                modes=[],
                jacks=[],
            )
        ],
    )

    sig = detect_signatures(canon_vl2)
    assert sig["has_vl2"] is True

    reg = build_registry_for_rig(canon_vl2)
    # Ensure at least one VL2 micro template exists
    vl2_templates = [t for t in reg.templates if t.template_id.startswith("vl2.")]
    assert len(vl2_templates) > 0

    # Check for specific VL2 micro-grammar templates
    micro_templates = [t for t in reg.templates if "micro" in t.template_id or "bus" in t.template_id or "macro" in t.template_id]
    assert len(micro_templates) > 0


def test_non_vl2_registry_excludes_micro_grammar():
    """Test that VL2 micro-grammar templates are NOT activated for non-VL2 rigs."""
    canon_generic = CanonicalRig(
        rig_id="rig.generic.test",
        modules=[
            CanonicalModule(
                instance_id="inst.01",
                name="Generic Oscillator",
                hp=8,
                tags=[],
                modes=[],
                jacks=[],
            )
        ],
    )

    sig = detect_signatures(canon_generic)
    assert sig["has_vl2"] is False

    reg = build_registry_for_rig(canon_generic)

    # VL2 pack v1 templates should still be there (they work for any rig)
    vl2_pack_templates = [t for t in reg.templates if t.template_id.startswith("vl2.") and "pack" in t.template_id or "voice" in t.template_id or "generative" in t.template_id]

    # But VL2 micro-grammar specific templates should NOT be there
    # These are the ones that require VL2-specific jacks
    micro_only_templates = [t for t in reg.templates if "bus.clock_distribution" in t.template_id or "macro.env_to_vca" in t.template_id or "clock_to_snh" in t.template_id]
    assert len(micro_only_templates) == 0
