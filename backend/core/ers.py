"""
ERS (Entropy-Reduction Scheduler) Integration for PatchHive.

ERS is a scheduling abstraction for heavy operations that can be:
- Run synchronously (default, simple)
- Queued for background execution (future)
- Distributed across workers (future)

This module provides:
- Job descriptors for schedulable operations
- Simple synchronous executor (default)
- Hooks for future async/distributed execution

Complexity note: This adds a thin scheduling layer that enables future
optimization without changing application code (satisfies ABX-Core v1.3
complexity rule: adds flexibility with minimal overhead).
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Callable, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid

JobType = Literal["patch_generation", "pdf_export", "svg_export", "rack_validation"]
JobStatus = Literal["pending", "running", "completed", "failed"]


class JobPriority(Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ERSJob:
    """
    Descriptor for a schedulable job.

    This is a lightweight job descriptor that can be:
    - Executed immediately (sync mode)
    - Queued for background processing
    - Distributed to workers

    The job doesn't contain the actual work function,
    just metadata about what needs to be done.
    """
    job_id: str  # Unique job ID
    job_type: JobType  # Type of job
    priority: JobPriority = JobPriority.NORMAL

    # Status tracking
    status: JobStatus = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Job parameters (serializable)
    params: Dict[str, Any] = field(default_factory=dict)

    # Result (after completion)
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    # Scheduling hints
    estimated_duration_ms: Optional[float] = None
    requires_gpu: bool = False
    requires_network: bool = False

    def mark_started(self) -> None:
        """Mark job as started."""
        self.status = "running"
        self.started_at = datetime.now(timezone.utc).isoformat()

    def mark_completed(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark job as completed."""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.result = result

    def mark_failed(self, error_message: str) -> None:
        """Mark job as failed."""
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["priority"] = self.priority.value
        return data

    @classmethod
    def create(
        cls,
        job_type: JobType,
        params: Dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        estimated_duration_ms: Optional[float] = None
    ) -> "ERSJob":
        """Factory method to create a new job."""
        return cls(
            job_id=str(uuid.uuid4()),
            job_type=job_type,
            priority=priority,
            params=params,
            estimated_duration_ms=estimated_duration_ms
        )


# Job registry (in-memory, can be extended to Redis/DB)
_job_registry: Dict[str, ERSJob] = {}


def register_job(job: ERSJob) -> str:
    """
    Register a job in the registry.

    Returns:
        job_id
    """
    _job_registry[job.job_id] = job
    return job.job_id


def get_job(job_id: str) -> Optional[ERSJob]:
    """Get a job by ID."""
    return _job_registry.get(job_id)


def get_pending_jobs(limit: int = 100) -> list[ERSJob]:
    """
    Get pending jobs, ordered by priority.

    This is used by workers to pull jobs from the queue.
    """
    pending = [j for j in _job_registry.values() if j.status == "pending"]
    # Sort by priority (high to low), then by created_at (old to new)
    pending.sort(key=lambda j: (-j.priority.value, j.created_at))
    return pending[:limit]


def clear_job_registry() -> None:
    """Clear the job registry (for testing)."""
    global _job_registry
    _job_registry = {}


class ERSExecutor:
    """
    Simple synchronous executor for ERS jobs.

    This is the default executor that runs jobs immediately.
    Future implementations can add async/distributed execution.
    """

    @staticmethod
    def execute_sync(job: ERSJob, work_fn: Callable[[Dict[str, Any]], Any]) -> Any:
        """
        Execute a job synchronously.

        Args:
            job: Job descriptor
            work_fn: Function that performs the work, takes job.params as input

        Returns:
            Result of work_fn
        """
        job.mark_started()

        try:
            result = work_fn(job.params)
            job.mark_completed({"result": result})
            return result

        except Exception as e:
            job.mark_failed(str(e))
            raise

    @staticmethod
    def queue_async(job: ERSJob) -> str:
        """
        Queue a job for asynchronous execution.

        In the current implementation, this just registers the job.
        Future implementations can integrate with Celery, RQ, or custom workers.

        Returns:
            job_id
        """
        register_job(job)
        # TODO: Integrate with actual async queue (Celery, RQ, etc.)
        return job.job_id


# Convenience functions for common operations
def schedule_patch_generation(
    rack_id: int,
    seed: int,
    priority: JobPriority = JobPriority.NORMAL
) -> ERSJob:
    """
    Schedule a patch generation job.

    Args:
        rack_id: ID of rack to generate patches for
        seed: Random seed
        priority: Job priority

    Returns:
        Job descriptor
    """
    job = ERSJob.create(
        job_type="patch_generation",
        params={"rack_id": rack_id, "seed": seed},
        priority=priority,
        estimated_duration_ms=1000.0  # Estimate: 1 second
    )
    register_job(job)
    return job


def schedule_pdf_export(
    patch_id: int,
    priority: JobPriority = JobPriority.NORMAL
) -> ERSJob:
    """
    Schedule a PDF export job.

    Args:
        patch_id: ID of patch to export
        priority: Job priority

    Returns:
        Job descriptor
    """
    job = ERSJob.create(
        job_type="pdf_export",
        params={"patch_id": patch_id},
        priority=priority,
        estimated_duration_ms=2000.0  # Estimate: 2 seconds
    )
    register_job(job)
    return job


def schedule_svg_export(
    patch_id: int,
    priority: JobPriority = JobPriority.NORMAL
) -> ERSJob:
    """
    Schedule an SVG export job.

    Args:
        patch_id: ID of patch to export
        priority: Job priority

    Returns:
        Job descriptor
    """
    job = ERSJob.create(
        job_type="svg_export",
        params={"patch_id": patch_id},
        priority=priority,
        estimated_duration_ms=500.0  # Estimate: 500ms
    )
    register_job(job)
    return job
