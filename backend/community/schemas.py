"""
Pydantic schemas for Community API (users, auth, votes, comments).
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    """Base schema for user data."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    avatar_url: Optional[str] = None
    display_name: Optional[str] = Field(default=None, max_length=100)
    allow_public_avatar: bool = True
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    avatar_url: Optional[str] = None
    display_name: Optional[str] = Field(default=None, max_length=100)
    allow_public_avatar: Optional[bool] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for auth token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Vote schemas
class VoteCreate(BaseModel):
    """Schema for creating a vote."""

    rack_id: Optional[int] = None
    patch_id: Optional[int] = None


class VoteResponse(BaseModel):
    """Schema for vote response."""

    id: int
    user_id: int
    rack_id: Optional[int]
    patch_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Comment schemas
class CommentBase(BaseModel):
    """Base schema for comment data."""

    content: str = Field(..., min_length=1, max_length=2000)


class CommentCreate(CommentBase):
    """Schema for creating a comment."""

    rack_id: Optional[int] = None
    patch_id: Optional[int] = None


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""

    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(CommentBase):
    """Schema for comment response."""

    id: int
    user_id: int
    rack_id: Optional[int]
    patch_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


# Feed schemas
class FeedItem(BaseModel):
    """Schema for a feed item (rack or patch)."""

    type: str  # "rack" or "patch"
    id: int
    name: str
    description: Optional[str]
    user: UserResponse
    vote_count: int
    created_at: datetime


class FeedResponse(BaseModel):
    """Schema for feed response."""

    total: int
    items: list[FeedItem]
