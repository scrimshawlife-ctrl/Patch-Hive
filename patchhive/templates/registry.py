from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TemplateSlot:
    """
    A connection slot in a patch template.
    Defines: from_role -> to_role with signal type.
    """
    from_role: str
    to_role: str
    signal_type: str  # e.g., "audio", "cv", "clock", "gate"


@dataclass(frozen=True)
class PatchTemplate:
    """
    A reusable patch template with typed slots and constraints.
    """
    template_id: str
    archetype: str  # e.g., "utility_clock_bus", "generative_vl2"
    category: str  # PatchCategory value as string
    difficulty: str  # PatchDifficulty value as string
    tags: Tuple[str, ...]
    slots: Tuple[TemplateSlot, ...]
    role_constraints: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    required_functions: Optional[Dict[str, 'RequireFn']] = None  # forward ref


class PatchTemplateRegistry:
    """
    Registry of patch templates.
    Allows conditional activation of template sets (e.g., VL2-specific templates).
    """
    def __init__(self):
        self.templates: List[PatchTemplate] = []

    def register(self, template: PatchTemplate) -> None:
        self.templates.append(template)

    def get_by_archetype(self, archetype: str) -> List[PatchTemplate]:
        return [t for t in self.templates if t.archetype == archetype]

    def get_by_id(self, template_id: str) -> Optional[PatchTemplate]:
        for t in self.templates:
            if t.template_id == template_id:
                return t
        return None


def build_default_registry() -> PatchTemplateRegistry:
    """
    Build the default registry with basic templates.
    This is the baseline that works for any rig.
    """
    reg = PatchTemplateRegistry()

    # Basic templates (minimal set for now)
    reg.register(PatchTemplate(
        template_id="basic.voice.simple_osc_out.v1",
        archetype="basic_voice",
        category="Voice",
        difficulty="Beginner",
        tags=("basic", "voice", "oscillator"),
        slots=(
            TemplateSlot("OSC_OUT", "OUTPUT", "audio"),
        ),
        role_constraints={
            "OSC_OUT": ("audio_out",),
            "OUTPUT": ("audio_in_or_cv_or_audio_in",),
        },
    ))

    reg.register(PatchTemplate(
        template_id="basic.generative.random_mod.v1",
        archetype="generative_mod",
        category="Generative",
        difficulty="Advanced",
        tags=("generative", "random", "modulation"),
        slots=(
            TemplateSlot("RANDOM_OUT", "MOD_IN", "cv"),
        ),
        role_constraints={
            "RANDOM_OUT": ("cv_out",),
            "MOD_IN": ("cv_in_or_cv_or_audio_in",),
        },
    ))

    reg.register(PatchTemplate(
        template_id="basic.clocked.clock_to_seq.v1",
        archetype="clocked_sequence",
        category="Clock-Rhythm",
        difficulty="Intermediate",
        tags=("clocked", "sequencer"),
        slots=(
            TemplateSlot("CLOCK_OUT", "SEQ_CLOCK_IN", "clock"),
        ),
        role_constraints={
            "CLOCK_OUT": ("clock_out",),
            "SEQ_CLOCK_IN": ("clock_in",),
        },
    ))

    return reg
