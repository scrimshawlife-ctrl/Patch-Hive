"""
FastAPI routes for Community features (users, auth, votes, comments, feed).
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from account.models import Referral
from account.services import ensure_referral_code
from core import create_access_token, get_db, get_password_hash, verify_password
from monetization.referrals import create_referral, generate_referral_code, get_referral_summary
from monetization.schemas import ReferralSummary
from patches.models import Patch
from racks.models import Rack

from .auth import get_current_user, require_auth
from .models import Comment, User, Vote
from .schemas import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    FeedItem,
    FeedResponse,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    VoteCreate,
    VoteResponse,
)

router = APIRouter()


# User routes
@router.post("/users", response_model=UserResponse, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check if email exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    referrer = None
    if user.referral_code:
        referrer = db.query(User).filter(User.referral_code == user.referral_code).first()
        if not referrer:
            raise HTTPException(status_code=400, detail="Invalid referral code")

    # Create user
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        display_name=user.display_name or user.username,
        role="User",
        referral_code=generate_referral_code(db, username=user.username, email=user.email),
        referred_by=referrer.id if referrer else None,
        avatar_url=user.avatar_url,
        allow_public_avatar=user.allow_public_avatar,
        bio=user.bio,
    )
    db.add(db_user)
    db.flush()
    if referrer:
        try:
            create_referral(db, referrer=referrer, referred=db_user)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(db_user)

    ensure_referral_code(db, db_user)

    if user.referral_code:
        referrer = db.query(User).filter(User.referral_code == user.referral_code).first()
        if referrer and referrer.id != db_user.id:
            existing_referral = (
                db.query(Referral).filter(Referral.referred_user_id == db_user.id).first()
            )
            if not existing_referral:
                referral = Referral(
                    referrer_user_id=referrer.id, referred_user_id=db_user.id, status="pending"
                )
                db.add(referral)
                db.commit()

    return db_user


@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token."""
    # Find user
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token
    token = create_access_token({"user_id": user.id, "username": user.username})

    return TokenResponse(access_token=token, user=user)


@router.get("/users/me", response_model=UserResponse)
def get_current_profile(current_user: User = Depends(require_auth)):
    """Get current user's profile."""
    return current_user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/username/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """Get user profile by username."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/me", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/users/me/referrals", response_model=ReferralSummary)
def get_referrals(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get referral summary for the current user."""
    summary = get_referral_summary(db, user=current_user)
    return ReferralSummary(
        referral_code=summary["referral_code"],
        referral_link=summary["referral_link"],
        earned_credits=summary["earned_credits"],
        pending_referrals=summary["pending_referrals"],
        rewarded_referrals=summary["rewarded_referrals"],
    )


# Vote routes
@router.post("/votes", response_model=VoteResponse, status_code=201)
def create_vote(
    vote: VoteCreate, current_user: User = Depends(require_auth), db: Session = Depends(get_db)
):
    """Create a vote (like) on a rack or patch."""
    # Validate that exactly one target is specified
    if not ((vote.rack_id is None) ^ (vote.patch_id is None)):
        raise HTTPException(
            status_code=400, detail="Must specify either rack_id or patch_id, not both"
        )

    # Check if already voted
    existing = (
        db.query(Vote)
        .filter(
            Vote.user_id == current_user.id,
            or_(Vote.rack_id == vote.rack_id, Vote.patch_id == vote.patch_id),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already voted")

    # Create vote
    db_vote = Vote(user_id=current_user.id, rack_id=vote.rack_id, patch_id=vote.patch_id)
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)

    return db_vote


@router.delete("/votes/{vote_id}", status_code=204)
def delete_vote(
    vote_id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)
):
    """Delete a vote."""
    vote = db.query(Vote).filter(Vote.id == vote_id, Vote.user_id == current_user.id).first()
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")

    db.delete(vote)
    db.commit()
    return None


# Comment routes
@router.post("/comments", response_model=CommentResponse, status_code=201)
def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Create a comment on a rack or patch."""
    # Validate that exactly one target is specified
    if not ((comment.rack_id is None) ^ (comment.patch_id is None)):
        raise HTTPException(
            status_code=400, detail="Must specify either rack_id or patch_id, not both"
        )

    db_comment = Comment(
        user_id=current_user.id,
        rack_id=comment.rack_id,
        patch_id=comment.patch_id,
        content=comment.content,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    # Attach user
    db_comment.user = current_user

    return db_comment


@router.get("/comments", response_model=list[CommentResponse])
def list_comments(
    rack_id: Optional[int] = None,
    patch_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List comments."""
    query = db.query(Comment)

    if rack_id is not None:
        query = query.filter(Comment.rack_id == rack_id)
    if patch_id is not None:
        query = query.filter(Comment.patch_id == patch_id)

    comments = query.order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()

    # Attach users
    for comment in comments:
        comment.user = db.query(User).filter(User.id == comment.user_id).first()

    return comments


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Update a comment."""
    db_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.user_id == current_user.id)
        .first()
    )
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db_comment.content = comment_update.content
    db.commit()
    db.refresh(db_comment)

    db_comment.user = current_user

    return db_comment


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int, current_user: User = Depends(require_auth), db: Session = Depends(get_db)
):
    """Delete a comment."""
    db_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.user_id == current_user.id)
        .first()
    )
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(db_comment)
    db.commit()
    return None


# Feed route
@router.get("/feed", response_model=FeedResponse)
def get_feed(
    skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
):
    """Get public feed of shared racks and patches."""
    # Get public racks
    racks = db.query(Rack).filter(Rack.is_public.is_(True)).order_by(desc(Rack.created_at)).all()

    # Get public patches
    patches = (
        db.query(Patch).filter(Patch.is_public.is_(True)).order_by(desc(Patch.created_at)).all()
    )

    # Build feed items
    feed_items: list[FeedItem] = []

    for rack in racks:
        user = db.query(User).filter(User.id == rack.user_id).first()
        vote_count = db.query(Vote).filter(Vote.rack_id == rack.id).count()

        feed_items.append(
            FeedItem(
                type="rack",
                id=rack.id,
                name=rack.name,
                description=rack.description,
                user=user,
                vote_count=vote_count,
                created_at=rack.created_at,
            )
        )

    for patch in patches:
        rack = db.query(Rack).filter(Rack.id == patch.rack_id).first()
        if not rack:
            continue

        user = db.query(User).filter(User.id == rack.user_id).first()
        vote_count = db.query(Vote).filter(Vote.patch_id == patch.id).count()

        feed_items.append(
            FeedItem(
                type="patch",
                id=patch.id,
                name=patch.name,
                description=patch.description,
                user=user,
                vote_count=vote_count,
                created_at=patch.created_at,
            )
        )

    # Sort by created_at
    feed_items.sort(key=lambda x: x.created_at, reverse=True)

    # Paginate
    total = len(feed_items)
    feed_items = feed_items[skip : skip + limit]

    return FeedResponse(total=total, items=feed_items)
