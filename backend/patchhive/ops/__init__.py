"""PatchHive operations for append-only stores and deterministic derivations."""

from .build_patch_library import build_patch_library
from .commit_function_registry import confirm_and_commit_function
from .commit_jack_function_to_module import bind_function_id_to_jack_append_only
from .commit_module_image import attach_module_image_append_only
from .derive_symbolic_envelope import derive_symbolic_envelope
from .generate_patch_candidates import generate_patch_candidates
from .name_patch import categorize_patch, difficulty_from_cables, name_patch
from .validate_patch import validate_patch

__all__ = [
    "attach_module_image_append_only",
    "bind_function_id_to_jack_append_only",
    "confirm_and_commit_function",
    "build_patch_library",
    "derive_symbolic_envelope",
    "generate_patch_candidates",
    "categorize_patch",
    "difficulty_from_cables",
    "name_patch",
    "validate_patch",
]
