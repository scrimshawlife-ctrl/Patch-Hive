"""
SQLAlchemy models for community features (users, votes, comments).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default="User", index=True)
    referral_code = Column(String(32), unique=True, nullable=False, index=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    racks = relationship("Rack", back_populates="user", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    referrer = relationship("User", remote_side=[id], backref="referrals")


class Vote(Base):
    """Vote/like on a rack or patch."""

    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rack_id = Column(Integer, ForeignKey("racks.id", ondelete="CASCADE"), nullable=True)
    patch_id = Column(Integer, ForeignKey("patches.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="votes")
    rack = relationship("Rack", back_populates="votes")
    patch = relationship("Patch", back_populates="votes")

    # Constraints: user can only vote once per item
    __table_args__ = (
        UniqueConstraint("user_id", "rack_id", name="unique_user_rack_vote"),
        UniqueConstraint("user_id", "patch_id", name="unique_user_patch_vote"),
    )


class Comment(Base):
    """Comment on a rack or patch."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rack_id = Column(Integer, ForeignKey("racks.id", ondelete="CASCADE"), nullable=True)
    patch_id = Column(Integer, ForeignKey("patches.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="comments")
    rack = relationship("Rack", back_populates="comments")
    patch = relationship("Patch", back_populates="comments")
