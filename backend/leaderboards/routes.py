"""Public leaderboards for module popularity."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from core import get_db
from modules.models import Module
from racks.models import RackModule, Rack
from account.schemas import LeaderboardEntryResponse

router = APIRouter()


_CACHE: dict[str, dict[str, object]] = {}
_CACHE_TTL_SECONDS = 60 * 30


def _get_cached(key: str) -> Optional[list[LeaderboardEntryResponse]]:
    cached = _CACHE.get(key)
    if not cached:
        return None
    if datetime.utcnow() - cached["timestamp"] > timedelta(seconds=_CACHE_TTL_SECONDS):
        _CACHE.pop(key, None)
        return None
    return cached["value"]


def _set_cache(key: str, value: list[LeaderboardEntryResponse]) -> None:
    _CACHE[key] = {"timestamp": datetime.utcnow(), "value": value}


def _build_leaderboard(rows) -> list[LeaderboardEntryResponse]:
    return [
        LeaderboardEntryResponse(
            rank=index + 1,
            module_name=row.name,
            manufacturer=row.brand,
            count=row.count,
        )
        for index, row in enumerate(rows)
    ]


@router.get("/modules/popular", response_model=list[LeaderboardEntryResponse])
def get_popular_modules(db: Session = Depends(get_db)):
    """Get most popular modules by rack appearances."""
    cache_key = "modules_popular"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    rows = (
        db.query(
            Module.name.label("name"),
            Module.brand.label("brand"),
            func.count(RackModule.id).label("count"),
        )
        .join(RackModule, RackModule.module_id == Module.id)
        .join(Rack, Rack.id == RackModule.rack_id)
        .filter(Rack.is_public.is_(True))
        .group_by(Module.id)
        .order_by(desc("count"))
        .limit(50)
        .all()
    )

    leaderboard = _build_leaderboard(rows)
    _set_cache(cache_key, leaderboard)
    return leaderboard


@router.get("/modules/trending", response_model=list[LeaderboardEntryResponse])
def get_trending_modules(
    window_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get trending modules by rack appearances within a time window."""
    cache_key = f"modules_trending_{window_days}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    cutoff = datetime.utcnow() - timedelta(days=window_days)

    rows = (
        db.query(
            Module.name.label("name"),
            Module.brand.label("brand"),
            func.count(RackModule.id).label("count"),
        )
        .join(RackModule, RackModule.module_id == Module.id)
        .join(Rack, Rack.id == RackModule.rack_id)
        .filter(Rack.created_at >= cutoff, Rack.is_public.is_(True))
        .group_by(Module.id)
        .order_by(desc("count"))
        .limit(50)
        .all()
    )

    leaderboard = _build_leaderboard(rows)
    _set_cache(cache_key, leaderboard)
    return leaderboard
