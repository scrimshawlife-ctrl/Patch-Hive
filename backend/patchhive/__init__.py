"""PatchHive canonical subsystem."""

from .schemas import (
    DetectedModule,
    ResolvedModuleRef,
    ModuleGalleryEntry,
    RigSpec,
    CanonicalRig,
    RigMetricsPacket,
    SuggestedLayout,
    PatchGraph,
    PatchPlan,
    ValidationReport,
    SymbolicPatchEnvelope,
)
from .ops.detect_from_photo import detect_modules_from_photo
from .ops.resolve_modules import resolve_modules
from .ops.ensure_specs import ensure_module_specs
from .ops.ensure_gallery_sketch import ensure_sketch
from .ops.build_canonical_rig import build_canonical_rig
from .ops.map_metrics import map_metrics
from .ops.suggest_layouts import suggest_layouts
from .ops.generate_patch import generate_patch
from .ops.validate_patch import validate_patch

__all__ = [
    "DetectedModule",
    "ResolvedModuleRef",
    "ModuleGalleryEntry",
    "RigSpec",
    "CanonicalRig",
    "RigMetricsPacket",
    "SuggestedLayout",
    "PatchGraph",
    "PatchPlan",
    "ValidationReport",
    "SymbolicPatchEnvelope",
    "detect_modules_from_photo",
    "resolve_modules",
    "ensure_module_specs",
    "ensure_sketch",
    "build_canonical_rig",
    "map_metrics",
    "suggest_layouts",
    "generate_patch",
    "validate_patch",
]
