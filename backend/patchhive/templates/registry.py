from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TemplateSlot:
    """
    A slot describes a required connection from a role to a role.
    """

    role_out: str
    role_in: str
    cable_type: str


@dataclass(frozen=True)
class PatchTemplate:
    template_id: str
    archetype: str
    category: str
    difficulty: str
    tags: Tuple[str, ...]
    slots: Tuple[TemplateSlot, ...]
    role_constraints: Dict[str, Tuple[str, ...]]
    post_filter: Optional[Callable[[Dict[str, str]], bool]] = None


class PatchTemplateRegistry:
    def __init__(self) -> None:
        self._templates: Dict[str, PatchTemplate] = {}

    def register(self, template: PatchTemplate) -> None:
        if template.template_id in self._templates:
            raise ValueError(f"Template already registered: {template.template_id}")
        self._templates[template.template_id] = template

    def all(self) -> List[PatchTemplate]:
        return [self._templates[key] for key in sorted(self._templates.keys())]


def build_default_registry() -> PatchTemplateRegistry:
    """
    v1 templates: simple but combinatorially productive.
    """
    registry = PatchTemplateRegistry()

    registry.register(
        PatchTemplate(
            template_id="tmpl.voice.basic_path.v1",
            archetype="basic_voice",
            category="Voice",
            difficulty="Beginner",
            tags=("voice", "audio_path", "monitoring"),
            slots=(TemplateSlot("SOURCE_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),),
            role_constraints={
                "SOURCE_AUDIO_OUT": ("audio_out",),
                "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            },
        )
    )

    registry.register(
        PatchTemplate(
            template_id="tmpl.generative.audio_plus_mod.v1",
            archetype="generative_mod",
            category="Generative",
            difficulty="Intermediate",
            tags=("generative", "motion", "modulation"),
            slots=(
                TemplateSlot("SOURCE_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
                TemplateSlot("MOD_CV_OUT", "MOD_DEST_CV_IN", "cv"),
            ),
            role_constraints={
                "SOURCE_AUDIO_OUT": ("audio_out",),
                "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
                "MOD_CV_OUT": ("cv_out",),
                "MOD_DEST_CV_IN": ("cv_in_or_cv_or_audio_in",),
            },
        )
    )

    registry.register(
        PatchTemplate(
            template_id="tmpl.clocked.clock_plus_audio.v1",
            archetype="clocked_sequence",
            category="Clocked",
            difficulty="Intermediate",
            tags=("clocked", "sequence", "tempo"),
            slots=(
                TemplateSlot("CLOCK_OUT", "CLOCK_IN", "clock"),
                TemplateSlot("SOURCE_AUDIO_OUT", "DEST_AUDIO_IN", "audio"),
            ),
            role_constraints={
                "CLOCK_OUT": ("clock_out",),
                "CLOCK_IN": ("clock_in",),
                "SOURCE_AUDIO_OUT": ("audio_out",),
                "DEST_AUDIO_IN": ("audio_in_or_cv_or_audio_in",),
            },
        )
    )

    return registry
