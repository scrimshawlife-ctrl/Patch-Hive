from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class TemplateSlot:
    source_role: str
    dest_role: str
    signal_kind: str


@dataclass(frozen=True)
class PatchTemplate:
    template_id: str
    archetype: str
    category: str
    difficulty: str
    tags: Tuple[str, ...]
    slots: Tuple[TemplateSlot, ...]
    role_constraints: Dict[str, Tuple[str, ...]]
    required_caps: Optional[Dict[str, Tuple[str, ...]]] = None


class PatchTemplateRegistry:
    def __init__(self) -> None:
        self._templates: List[PatchTemplate] = []

    def register(self, template: PatchTemplate) -> None:
        self._templates.append(template)

    def templates(self) -> Iterable[PatchTemplate]:
        return list(self._templates)


def build_default_registry() -> PatchTemplateRegistry:
    return PatchTemplateRegistry()
