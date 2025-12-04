"""
Provenance tracking for ABX-Core v1.3 compliance.

Provenance captures the complete lineage of generated artifacts, satisfying
the SEED principle's requirement for full traceability.

Every generated patch must have provenance metadata that includes:
- run_id (unique identifier for generation run)
- timestamps
- version information
- host/environment info
- metrics

This module provides lightweight, zero-overhead provenance tracking that
reduces operational entropy (ABX-Core v1.3 complexity rule).
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Literal
from datetime import datetime, timezone
import uuid
import os
import socket

PipelineType = Literal["patch_generation", "rack_layout", "export", "import"]


@dataclass
class ProvenanceMetrics:
    """Optional metrics captured during execution."""
    duration_ms: Optional[float] = None
    cpu_time_ms: Optional[float] = None
    patch_count: Optional[int] = None
    connection_count: Optional[int] = None
    memory_mb: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Provenance:
    """
    Complete provenance record for a generated artifact.

    ABX-Core v1.3 requirement: All generated artifacts must have traceable
    provenance that enables full replay and debugging.
    """
    # Core identifiers
    run_id: str  # UUID for this specific run
    entity_type: str  # "patch", "rack", "export", etc.
    entity_id: Optional[str] = None  # ID of the generated entity (set after creation)

    # Version tracking
    abx_core_version: str = "1.3"
    engine_version: str = "1.3.0"
    git_commit: Optional[str] = None

    # Timestamps (ISO8601 UTC)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None

    # Environment
    host: str = field(default_factory=lambda: socket.gethostname())
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))

    # Pipeline info
    pipeline: PipelineType = "patch_generation"

    # Metrics (optional, populated during execution)
    metrics: ProvenanceMetrics = field(default_factory=ProvenanceMetrics)

    # Parent provenance (for derived artifacts)
    parent_run_id: Optional[str] = None

    def mark_completed(self) -> None:
        """Mark the provenance record as completed."""
        self.completed_at = datetime.now(timezone.utc).isoformat()

    def set_entity_id(self, entity_id: str) -> None:
        """Set the entity ID after creation."""
        self.entity_id = entity_id

    def add_metric(self, key: str, value: Any) -> None:
        """Add a custom metric."""
        setattr(self.metrics, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        # Filter out None values for cleaner storage
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def create(
        cls,
        entity_type: str,
        pipeline: PipelineType = "patch_generation",
        parent_run_id: Optional[str] = None,
        engine_version: str = "1.3.0",
        git_commit: Optional[str] = None
    ) -> "Provenance":
        """
        Factory method to create a new provenance record.

        This is the recommended way to create provenance records.
        """
        return cls(
            run_id=str(uuid.uuid4()),
            entity_type=entity_type,
            pipeline=pipeline,
            parent_run_id=parent_run_id,
            engine_version=engine_version,
            git_commit=git_commit or os.getenv("GIT_COMMIT")
        )


def get_git_commit() -> Optional[str]:
    """
    Get current git commit hash from environment or git command.

    Returns None if not available (not critical for provenance).
    """
    # Try environment variable first (set by CI/CD)
    commit = os.getenv("GIT_COMMIT")
    if commit:
        return commit[:8]  # Short hash

    # Try reading from .git (local development)
    try:
        git_head = os.path.join(os.path.dirname(__file__), "../../.git/HEAD")
        if os.path.exists(git_head):
            with open(git_head, "r") as f:
                ref = f.read().strip()
                if ref.startswith("ref:"):
                    ref_path = ref.split(" ")[1]
                    ref_file = os.path.join(os.path.dirname(__file__), f"../../.git/{ref_path}")
                    if os.path.exists(ref_file):
                        with open(ref_file, "r") as rf:
                            return rf.read().strip()[:8]
    except Exception:
        pass

    return None
