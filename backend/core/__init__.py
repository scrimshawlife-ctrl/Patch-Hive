"""Core utilities and configuration for PatchHive backend."""

from .config import settings
from .database import Base, get_db, init_db
from .discovery import FunctionDescriptor, get_registered_functions, register_function
from .ers import ERSExecutor, ERSJob, JobPriority, schedule_patch_generation, schedule_pdf_export
from .ir import (
    ConnectionIR,
    ModuleIR,
    PatchCategory,
    PatchGenerationIR,
    PatchGenerationParams,
    PatchGraphIR,
    RackStateIR,
)
from .naming import (
    generate_patch_name,
    generate_rack_name,
    generate_rig_suggested_name,
    hash_string_to_seed,
    name_patch_v2,
)
from .provenance import Provenance, ProvenanceMetrics, get_git_commit
from .runes import RuneContext, RuneTag, RuneTypes, get_recent_runes, with_rune
from .security import create_access_token, decode_access_token, get_password_hash, verify_password

__all__ = [
    "settings",
    "Base",
    "get_db",
    "init_db",
    "create_access_token",
    "decode_access_token",
    "get_password_hash",
    "verify_password",
    "generate_rack_name",
    "generate_patch_name",
    "generate_rig_suggested_name",
    "name_patch_v2",
    "hash_string_to_seed",
    # Provenance (ABX-Core v1.3)
    "Provenance",
    "ProvenanceMetrics",
    "get_git_commit",
    # IR (ABX-Core v1.3)
    "PatchGenerationIR",
    "RackStateIR",
    "ModuleIR",
    "PatchGenerationParams",
    "PatchGraphIR",
    "ConnectionIR",
    "PatchCategory",
    # ABX-Runes
    "RuneTag",
    "RuneContext",
    "with_rune",
    "RuneTypes",
    "get_recent_runes",
    # ERS
    "ERSJob",
    "ERSExecutor",
    "JobPriority",
    "schedule_patch_generation",
    "schedule_pdf_export",
    # Dynamic Function Discovery
    "FunctionDescriptor",
    "register_function",
    "get_registered_functions",
]
