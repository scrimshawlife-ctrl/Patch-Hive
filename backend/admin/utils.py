"""
Admin utilities for audit logging.
"""

from typing import Any, Optional

from sqlalchemy.orm import Session

from admin.models import AdminAuditLog
from community.models import User


def log_admin_action(
    db: Session,
    *,
    actor: User,
    action_type: str,
    target_type: str,
    target_id: Optional[str] = None,
    delta_json: Optional[dict[str, Any]] = None,
    reason: Optional[str] = None,
) -> AdminAuditLog:
    """Append an admin audit log entry."""
    entry = AdminAuditLog(
        actor_user_id=actor.id,
        actor_role=actor.role,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        delta_json=delta_json,
        reason=reason,
    )
    db.add(entry)
    return entry
