"""Simple in-process rate limiter for free Design Engine preview (KD-15)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from core.config import settings


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    retry_after_seconds: float
    remaining: int


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, *, limit: int, window_seconds: float) -> RateLimitResult:
        now = time.monotonic()
        with self._lock:
            q = self._events[key]
            cutoff = now - window_seconds
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= limit:
                retry = window_seconds - (now - q[0]) if q else window_seconds
                return RateLimitResult(
                    allowed=False, retry_after_seconds=max(0.0, retry), remaining=0
                )
            q.append(now)
            return RateLimitResult(
                allowed=True,
                retry_after_seconds=0.0,
                remaining=max(0, limit - len(q)),
            )


_PREVIEW_LIMITER = SlidingWindowLimiter()


def check_preview_rate_limit(user_id: int) -> RateLimitResult:
    limit = int(getattr(settings, "preview_rate_limit_per_minute", 30) or 30)
    return _PREVIEW_LIMITER.check(f"preview:{user_id}", limit=limit, window_seconds=60.0)


def reset_preview_rate_limits_for_tests() -> None:
    with _PREVIEW_LIMITER._lock:
        _PREVIEW_LIMITER._events.clear()
