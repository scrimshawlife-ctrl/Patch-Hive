"""
ABX-Runes: Lightweight operation tagging for the AAL ecosystem.

Runes are lightweight markers that tag operations with metadata for
observability, scheduling, and cross-service correlation.

This module provides:
- Rune tagging decorators
- Operation timing and metadata collection
- Integration points for ERS (Entropy-Reduction Scheduler)

Complexity note: Runes add minimal overhead (~microseconds per operation)
while providing significant operational visibility (satisfies ABX-Core v1.3
complexity rule: new complexity reduces entropy).
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timezone
from functools import wraps
import time
import uuid

# Rune operation types (extensible)
RuneType = str  # "RACK_VALIDATE", "PATCH_GENERATE", "EXPORT_PDF", etc.


@dataclass
class RuneTag:
    """
    A rune tag attached to an operation.

    Runes are lightweight operation markers that carry metadata
    for observability and scheduling.
    """
    rune_id: str  # Unique ID for this rune instance
    rune_type: RuneType  # Operation type
    started_at: str  # ISO8601 UTC timestamp
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None

    # Operation metadata
    entity_type: Optional[str] = None  # "rack", "patch", "export"
    entity_id: Optional[str] = None
    parent_rune_id: Optional[str] = None  # For nested operations

    # Metrics (extensible)
    metrics: Dict[str, Any] = field(default_factory=dict)

    # Status
    success: bool = True
    error_message: Optional[str] = None

    def mark_completed(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """Mark the rune as completed."""
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.success = success
        self.error_message = error_message

        if self.started_at and self.completed_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            self.duration_ms = (end - start).total_seconds() * 1000

    def add_metric(self, key: str, value: Any) -> None:
        """Add a metric to the rune."""
        self.metrics[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    @classmethod
    def create(
        cls,
        rune_type: RuneType,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        parent_rune_id: Optional[str] = None
    ) -> "RuneTag":
        """Factory method to create a new rune tag."""
        return cls(
            rune_id=str(uuid.uuid4())[:8],  # Short ID
            rune_type=rune_type,
            started_at=datetime.now(timezone.utc).isoformat(),
            entity_type=entity_type,
            entity_id=entity_id,
            parent_rune_id=parent_rune_id
        )


# Global rune registry (in-memory, can be extended to use Redis/DB for persistence)
_rune_registry: List[RuneTag] = []
_max_registry_size = 1000  # Circular buffer


def register_rune(rune: RuneTag) -> None:
    """
    Register a rune in the global registry.

    The registry is a circular buffer that keeps the most recent runes.
    """
    global _rune_registry
    _rune_registry.append(rune)

    # Keep registry bounded
    if len(_rune_registry) > _max_registry_size:
        _rune_registry = _rune_registry[-_max_registry_size:]


def get_recent_runes(limit: int = 100, rune_type: Optional[RuneType] = None) -> List[RuneTag]:
    """
    Get recent runes from the registry.

    Args:
        limit: Maximum number of runes to return
        rune_type: Optional filter by rune type

    Returns:
        List of rune tags (most recent first)
    """
    runes = _rune_registry[-limit:]
    if rune_type:
        runes = [r for r in runes if r.rune_type == rune_type]
    return list(reversed(runes))


def clear_rune_registry() -> None:
    """Clear the rune registry (for testing)."""
    global _rune_registry
    _rune_registry = []


# Decorator for automatic rune tagging
def with_rune(
    rune_type: RuneType,
    entity_type: Optional[str] = None,
    entity_id_param: Optional[str] = None,  # Name of parameter to use as entity_id
    capture_result: bool = False
) -> Callable:
    """
    Decorator to automatically tag a function with a rune.

    Usage:
        @with_rune("PATCH_GENERATE", entity_type="patch", entity_id_param="patch_id")
        def generate_patch(patch_id: int) -> Patch:
            ...

    Args:
        rune_type: Type of rune
        entity_type: Type of entity being operated on
        entity_id_param: Name of function parameter to use as entity_id
        capture_result: Whether to capture return value in metrics

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract entity_id from parameters if specified
            entity_id = None
            if entity_id_param:
                # Try to get from kwargs
                entity_id = kwargs.get(entity_id_param)
                # Try to get from positional args (basic inspection)
                if entity_id is None and hasattr(func, "__code__"):
                    try:
                        param_names = func.__code__.co_varnames
                        if entity_id_param in param_names:
                            idx = param_names.index(entity_id_param)
                            if idx < len(args):
                                entity_id = args[idx]
                    except Exception:
                        pass

            # Convert entity_id to string if present
            if entity_id is not None:
                entity_id = str(entity_id)

            # Create rune
            rune = RuneTag.create(
                rune_type=rune_type,
                entity_type=entity_type,
                entity_id=entity_id
            )

            # Execute function
            try:
                result = func(*args, **kwargs)

                # Capture result if requested
                if capture_result:
                    rune.add_metric("result_type", type(result).__name__)
                    if hasattr(result, "__len__"):
                        rune.add_metric("result_count", len(result))

                rune.mark_completed(success=True)
                return result

            except Exception as e:
                rune.mark_completed(success=False, error_message=str(e))
                raise

            finally:
                register_rune(rune)

        return wrapper
    return decorator


# Context manager for manual rune tagging
class RuneContext:
    """
    Context manager for manual rune tagging.

    Usage:
        with RuneContext("EXPORT_PDF", entity_id=patch_id) as rune:
            # Do work
            rune.add_metric("pages", 10)
    """
    def __init__(
        self,
        rune_type: RuneType,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        parent_rune_id: Optional[str] = None
    ):
        self.rune = RuneTag.create(
            rune_type=rune_type,
            entity_type=entity_type,
            entity_id=entity_id,
            parent_rune_id=parent_rune_id
        )

    def __enter__(self) -> RuneTag:
        return self.rune

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.rune.mark_completed(success=True)
        else:
            self.rune.mark_completed(success=False, error_message=str(exc_val))
        register_rune(self.rune)
        return False  # Don't suppress exceptions


# Standard rune types for PatchHive operations
class RuneTypes:
    """Standard rune types used in PatchHive."""
    RACK_VALIDATE = "RACK_VALIDATE"
    RACK_CREATE = "RACK_CREATE"
    PATCH_GENERATE = "PATCH_GENERATE"
    PATCH_SAVE = "PATCH_SAVE"
    EXPORT_PDF = "EXPORT_PDF"
    EXPORT_SVG = "EXPORT_SVG"
    IMPORT_MODULARGRID = "IMPORT_MODULARGRID"
    API_REQUEST = "API_REQUEST"
