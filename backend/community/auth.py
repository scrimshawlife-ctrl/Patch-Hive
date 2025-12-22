"""Authentication helpers for community routes."""
from typing import Optional
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from core import get_db, decode_access_token
from .models import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("user_id")
    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()


def require_auth(current_user: Optional[User] = Depends(get_current_user)) -> User:
    """Require authentication."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


def require_admin(current_user: User = Depends(require_auth)) -> User:
    """Require admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
