"""
ResonanceFrame Export for Abraxas Oracle Integration.

This module exports PatchHive state as ResonanceFrames that Abraxas can ingest
for pattern analysis, anomaly detection, and oracle predictions.

ResonanceFrames are lightweight, privacy-preserving summaries of system state
that contain:
- Structural metrics (module counts, connection counts)
- Behavioral metrics (usage patterns, generation frequency)
- Entropy measures
- NO personally identifiable information
- NO sensitive secrets or auth tokens

Security principles:
- Read-only: No mutations to DB
- Privacy-first: Truncated seeds, hashed IDs where appropriate
- Minimal overhead: Simple queries, no complex joins

ABX-Core v1.3 compliance: This export mechanism reduces operational entropy
by providing Abraxas with structured, deterministic data for analysis.
"""

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from modules.models import Module
from patches.models import Patch
from racks.models import Rack

EntityType = Literal["patch", "rack", "module"]


@dataclass
class ResonanceFrame:
    """
    A resonance frame: a snapshot of an entity's state for Abraxas analysis.

    Frames are privacy-preserving and contain only structural/behavioral metrics.
    """

    # Identity
    entity_type: EntityType
    entity_id_hash: str  # Hashed entity ID (privacy-preserving)

    # Temporal
    created_at: str  # ISO8601 UTC
    age_seconds: float  # Age since creation

    # Structural metrics
    module_count: Optional[int] = None  # For racks/patches
    connection_count: Optional[int] = None  # For patches
    category: Optional[str] = None  # For patches

    # Behavioral metrics
    usage_count: int = 0  # Views, downloads, etc.
    is_public: bool = False

    # Entropy measures
    structural_entropy: float = 0.0  # Simple measure: connections / (modules^2)

    # Provenance (truncated/hashed)
    seed_hash: Optional[str] = None  # Truncated seed hash
    engine_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ResonanceExport:
    """
    Complete export of ResonanceFrames from PatchHive to Abraxas.

    This is the top-level object that gets sent to Abraxas.
    """

    # Metadata
    engine: str = "patchhive"
    version: str = "1.3.0"
    abx_core: str = "1.3"
    exported_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Frames
    frames: List[ResonanceFrame] = field(default_factory=list)

    # Summary stats
    total_patches: int = 0
    total_racks: int = 0
    total_modules: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "engine": self.engine,
            "version": self.version,
            "abx_core": self.abx_core,
            "exported_at": self.exported_at,
            "frames": [f.to_dict() for f in self.frames],
            "summary": {
                "total_patches": self.total_patches,
                "total_racks": self.total_racks,
                "total_modules": self.total_modules,
            },
        }


def hash_entity_id(entity_type: str, entity_id: int) -> str:
    """
    Create a privacy-preserving hash of an entity ID.

    Uses SHA256 with a type prefix for uniqueness.
    Returns truncated hash (16 chars).
    """
    key = f"{entity_type}:{entity_id}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def hash_seed(seed: int) -> str:
    """
    Create a truncated hash of a generation seed.

    Returns 8-char hex string.
    """
    return hashlib.sha256(str(seed).encode()).hexdigest()[:8]


def calculate_patch_entropy(connection_count: int, module_count: int) -> float:
    """
    Calculate structural entropy for a patch.

    Simple measure: connection_count / (module_count^2)
    Higher values = more complex/dense patch
    """
    if module_count < 2:
        return 0.0
    return connection_count / (module_count**2)


def export_patch_frames(db: Session, limit: int = 100) -> List[ResonanceFrame]:
    """
    Export recent patches as ResonanceFrames.

    Args:
        db: Database session
        limit: Max number of patches to export

    Returns:
        List of ResonanceFrames for patches
    """
    patches = db.query(Patch).order_by(desc(Patch.created_at)).limit(limit).all()

    frames: List[ResonanceFrame] = []

    for patch in patches:
        # Calculate age
        created = patch.created_at
        age_seconds = (datetime.utcnow() - created).total_seconds()

        # Calculate module count from connections
        module_ids = set()
        for conn in patch.connections:
            module_ids.add(conn.get("from_module_id"))
            module_ids.add(conn.get("to_module_id"))
        module_count = len(module_ids)

        # Calculate entropy
        connection_count = len(patch.connections)
        entropy = calculate_patch_entropy(connection_count, module_count)

        # Create frame
        frame = ResonanceFrame(
            entity_type="patch",
            entity_id_hash=hash_entity_id("patch", patch.id),
            created_at=created.isoformat(),
            age_seconds=age_seconds,
            module_count=module_count,
            connection_count=connection_count,
            category=patch.category,
            usage_count=0,  # TODO: Add usage tracking
            is_public=patch.is_public,
            structural_entropy=entropy,
            seed_hash=hash_seed(patch.generation_seed),
            engine_version=patch.generation_version,
        )
        frames.append(frame)

    return frames


def export_rack_frames(db: Session, limit: int = 100) -> List[ResonanceFrame]:
    """
    Export recent racks as ResonanceFrames.

    Args:
        db: Database session
        limit: Max number of racks to export

    Returns:
        List of ResonanceFrames for racks
    """
    from racks.models import RackModule

    racks = db.query(Rack).order_by(desc(Rack.created_at)).limit(limit).all()

    frames: List[ResonanceFrame] = []

    for rack in racks:
        # Count modules
        module_count = (
            db.query(func.count(RackModule.id)).filter(RackModule.rack_id == rack.id).scalar() or 0
        )

        # Calculate age
        created = rack.created_at
        age_seconds = (datetime.utcnow() - created).total_seconds()

        # Create frame
        frame = ResonanceFrame(
            entity_type="rack",
            entity_id_hash=hash_entity_id("rack", rack.id),
            created_at=created.isoformat(),
            age_seconds=age_seconds,
            module_count=module_count,
            usage_count=0,  # TODO: Add usage tracking
            is_public=rack.is_public,
            structural_entropy=0.0,  # Racks don't have entropy measure yet
        )
        frames.append(frame)

    return frames


def export_resonance_frames(
    db: Session, patch_limit: int = 100, rack_limit: int = 50
) -> ResonanceExport:
    """
    Export complete ResonanceFrame data for Abraxas.

    This is the main entry point for Abraxas integration.

    Args:
        db: Database session
        patch_limit: Max patches to export
        rack_limit: Max racks to export

    Returns:
        ResonanceExport object ready for serialization
    """
    # Export frames
    patch_frames = export_patch_frames(db, patch_limit)
    rack_frames = export_rack_frames(db, rack_limit)

    # Get summary stats
    total_patches = db.query(func.count(Patch.id)).scalar() or 0
    total_racks = db.query(func.count(Rack.id)).scalar() or 0
    total_modules = db.query(func.count(Module.id)).scalar() or 0

    # Build export
    export = ResonanceExport(
        frames=patch_frames + rack_frames,
        total_patches=total_patches,
        total_racks=total_racks,
        total_modules=total_modules,
    )

    return export


def export_resonance_frames_json(
    db: Session, patch_limit: int = 100, rack_limit: int = 50
) -> Dict[str, Any]:
    """
    Export ResonanceFrames as JSON-serializable dictionary.

    This is the most common format for API endpoints.

    Args:
        db: Database session
        patch_limit: Max patches to export
        rack_limit: Max racks to export

    Returns:
        JSON-serializable dictionary
    """
    export = export_resonance_frames(db, patch_limit, rack_limit)
    return export.to_dict()
