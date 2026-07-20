"""Canonical PatchHive MVP domain surface."""

from .contracts import *  # noqa: F403
from .compiler import compile_patch, validate_patch_graph

__all__ = ["compile_patch", "validate_patch_graph"]
