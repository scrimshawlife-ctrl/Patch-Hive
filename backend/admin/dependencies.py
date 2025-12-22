"""
Admin authorization dependencies.
"""
from fastapi import Depends, HTTPException

from community.models import User
from community.routes import require_auth

READ_ROLES = {"Admin", "Ops", "Support", "ReadOnly"}
MUTATE_ROLES = {"Admin", "Ops"}


def require_admin_read(current_user: User = Depends(require_auth)) -> User:
    """Require admin read access."""
    if current_user.role not in READ_ROLES:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_admin_mutate(current_user: User = Depends(require_auth)) -> User:
    """Require admin mutation access."""
    if current_user.role not in MUTATE_ROLES:
        raise HTTPException(status_code=403, detail="Admin mutation access required")
    return current_user
