"""Patch template registry for library generation."""

from .registry import PatchTemplate, PatchTemplateRegistry, TemplateSlot, build_default_registry

__all__ = [
    "PatchTemplate",
    "PatchTemplateRegistry",
    "TemplateSlot",
    "build_default_registry",
]
