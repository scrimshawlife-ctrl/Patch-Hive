from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from patchhive.templates.registry import PatchTemplateRegistry, PatchTemplate, TemplateSlot


@dataclass(frozen=True)
class RequireFn:
    """
    Function IDs required for a slot.
    If you don't have function_id mapping yet, this still works via alias matching in FunctionRegistry.
    """
    any_of: Tuple[str, ...]  # e.g., ("clock.out", "fn.unknown....")


def register_vl2_micro_grammar(reg: PatchTemplateRegistry) -> PatchTemplateRegistry:
    """
    Adds VL2-specific templates. These assume the VL2 module exposes a bunch of 'proprietary' points.
    We encode them as function IDs (or aliases) so they can be learned & normalized over time.
    """

    # 1) VL2 internal clock bus -> multiple destinations
    reg.register(PatchTemplate(
        template_id="vl2.bus.clock_distribution.v1",
        archetype="utility_clock_bus",
        category="Utility",
        difficulty="Beginner",
        tags=("vl2", "clock", "bus", "distribution"),
        slots=(
            TemplateSlot("VL2_CLOCK_OUT", "CLOCK_IN_A", "clock"),
            TemplateSlot("VL2_CLOCK_OUT", "CLOCK_IN_B", "clock"),
        ),
        role_constraints={
            "VL2_CLOCK_OUT": ("clock_out",),
            "CLOCK_IN_A": ("clock_in",),
            "CLOCK_IN_B": ("clock_in",),
        },
        # optional: function_id requirements (normalized over time)
        required_functions={
            "VL2_CLOCK_OUT": RequireFn(any_of=("clock.out", "vl2.clock.out",)),
        },
    ))

    # 2) VL2 random -> pitch + timbre macro
    reg.register(PatchTemplate(
        template_id="vl2.generative.random_pitch_timbre.v1",
        archetype="generative_vl2",
        category="Generative",
        difficulty="Advanced",
        tags=("vl2", "random", "pitch", "timbre"),
        slots=(
            TemplateSlot("VL2_RANDOM_OUT", "PITCH_IN", "cv"),
            TemplateSlot("VL2_RANDOM_OUT", "TIMBRE_CV_IN", "cv"),
            TemplateSlot("SOURCE_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
        ),
        role_constraints={
            "VL2_RANDOM_OUT": ("cv_out",),
            "PITCH_IN": ("cv_in_or_cv_or_audio_in",),
            "TIMBRE_CV_IN": ("cv_in_or_cv_or_audio_in",),
            "SOURCE_AUDIO_OUT": ("audio_out",),
            "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
        },
        required_functions={
            "VL2_RANDOM_OUT": RequireFn(any_of=("random.out", "vl2.random.out",)),
        },
    ))

    # 3) VL2 envelope macro -> multi-destination shaping (VCA + filter)
    reg.register(PatchTemplate(
        template_id="vl2.macro.env_to_vca_and_filter.v1",
        archetype="macro_shaping",
        category="Performance Macro",
        difficulty="Intermediate",
        tags=("vl2", "macro", "envelope", "shape"),
        slots=(
            TemplateSlot("VL2_ENV_OUT", "AMP_CV_IN", "cv"),
            TemplateSlot("VL2_ENV_OUT", "FILTER_CV_IN", "cv"),
            TemplateSlot("SOURCE_AUDIO_OUT", "AMP_AUDIO_IN", "audio"),
            TemplateSlot("AMP_AUDIO_OUT", "FILTER_AUDIO_IN", "audio"),
            TemplateSlot("FILTER_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
        ),
        role_constraints={
            "VL2_ENV_OUT": ("cv_out",),
            "AMP_CV_IN": ("cv_in_or_cv_or_audio_in",),
            "FILTER_CV_IN": ("cv_in_or_cv_or_audio_in",),
            "SOURCE_AUDIO_OUT": ("audio_out",),
            "AMP_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            "AMP_AUDIO_OUT": ("audio_out",),
            "FILTER_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            "FILTER_AUDIO_OUT": ("audio_out",),
            "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
        },
        required_functions={
            "VL2_ENV_OUT": RequireFn(any_of=("envelope.out", "vl2.env.out",)),
        },
    ))

    # 4) VL2 clocked modulation: clock -> sample/hold -> mod bus
    reg.register(PatchTemplate(
        template_id="vl2.generative.clock_to_snh_to_modbus.v1",
        archetype="clocked_mod_bus",
        category="Generative",
        difficulty="Advanced",
        tags=("vl2", "clocked", "snh", "modbus"),
        slots=(
            TemplateSlot("VL2_CLOCK_OUT", "SNH_CLOCK_IN", "clock"),
            TemplateSlot("VL2_RANDOM_OUT", "SNH_IN", "cv"),
            TemplateSlot("SNH_OUT", "MOD_DEST_CV_IN", "cv"),
        ),
        role_constraints={
            "VL2_CLOCK_OUT": ("clock_out",),
            "SNH_CLOCK_IN": ("clock_in",),
            "VL2_RANDOM_OUT": ("cv_out",),
            "SNH_IN": ("cv_in_or_cv_or_audio_in",),
            "SNH_OUT": ("cv_out",),
            "MOD_DEST_CV_IN": ("cv_in_or_cv_or_audio_in",),
        },
        required_functions={
            "VL2_CLOCK_OUT": RequireFn(any_of=("clock.out", "vl2.clock.out",)),
            "VL2_RANDOM_OUT": RequireFn(any_of=("random.out", "vl2.random.out",)),
        },
    ))

    return reg
