from __future__ import annotations

from patchhive.templates.registry import PatchTemplateRegistry, PatchTemplate, TemplateSlot


def register_vl2_pack_v1(reg: PatchTemplateRegistry) -> PatchTemplateRegistry:
    """
    VL2 Pack V1: Basic templates tailored for Voltage Lab 2 rigs.
    These work for any rig but are especially useful for VL2.
    """

    # Example VL2 template: basic voice patch
    reg.register(PatchTemplate(
        template_id="vl2.voice.basic_osc_vca.v1",
        archetype="basic_voice",
        category="Voice",
        difficulty="Beginner",
        tags=("vl2", "voice", "oscillator", "vca"),
        slots=(
            TemplateSlot("OSC_OUT", "VCA_IN", "audio"),
            TemplateSlot("VCA_OUT", "OUTPUT", "audio"),
        ),
        role_constraints={
            "OSC_OUT": ("audio_out",),
            "VCA_IN": ("audio_in_or_cv_or_audio_in",),
            "VCA_OUT": ("audio_out",),
            "OUTPUT": ("audio_in_or_cv_or_audio_in",),
        },
    ))

    # Example VL2 generative template
    reg.register(PatchTemplate(
        template_id="vl2.generative.random_modulation.v1",
        archetype="generative_mod",
        category="Generative",
        difficulty="Intermediate",
        tags=("vl2", "generative", "random"),
        slots=(
            TemplateSlot("RANDOM_OUT", "OSC_FM_IN", "cv"),
        ),
        role_constraints={
            "RANDOM_OUT": ("cv_out",),
            "OSC_FM_IN": ("cv_in_or_cv_or_audio_in",),
        },
    ))

    return reg
