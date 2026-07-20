"""Short-lived, principal-scoped download authorization for completed exports."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from canon.contracts import canonical_json

TOKEN_VERSION = "v1"
MAX_TTL_SECONDS = 15 * 60


class DownloadTokenError(ValueError):
    """Raised when an export download token cannot be trusted."""


@dataclass(frozen=True)
class DownloadGrant:
    export_id: str
    user_id: str
    expires_at: int


def _secret_key(secret: str) -> bytes:
    encoded = secret.encode("utf-8")
    if len(encoded) < 32:
        raise ValueError("download signing secret must contain at least 32 bytes")
    return encoded


def issue_download_token(
    *,
    export_id: str,
    user_id: str,
    secret: str,
    now: int | None = None,
    ttl_seconds: int = 5 * 60,
) -> str:
    """Issue an opaque token scoped to exactly one user and completed export."""

    if not export_id or not user_id:
        raise ValueError("export_id and user_id are required")
    if not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
        raise ValueError(f"ttl_seconds must be between 1 and {MAX_TTL_SECONDS}")
    issued_at = int(time.time()) if now is None else now
    payload = canonical_json(
        {
            "export_id": export_id,
            "expires_at": issued_at + ttl_seconds,
            "user_id": user_id,
        }
    ).encode("utf-8")
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")
    signature = hmac.new(_secret_key(secret), payload, hashlib.sha256).hexdigest()
    return f"{TOKEN_VERSION}.{encoded}.{signature}"


def verify_download_token(
    token: str,
    *,
    export_id: str,
    user_id: str,
    secret: str,
    now: int | None = None,
) -> DownloadGrant:
    """Verify integrity, expiry, and exact principal/resource scope."""

    try:
        version, encoded, supplied_signature = token.split(".")
        if version != TOKEN_VERSION:
            raise DownloadTokenError("unsupported download token version")
        padding = "=" * (-len(encoded) % 4)
        payload = base64.urlsafe_b64decode(encoded + padding)
        expected_signature = hmac.new(_secret_key(secret), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise DownloadTokenError("invalid download token signature")
        claims = json.loads(payload)
        grant = DownloadGrant(
            export_id=str(claims["export_id"]),
            user_id=str(claims["user_id"]),
            expires_at=int(claims["expires_at"]),
        )
    except DownloadTokenError:
        raise
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DownloadTokenError("malformed download token") from exc

    current_time = int(time.time()) if now is None else now
    if grant.expires_at < current_time:
        raise DownloadTokenError("download token has expired")
    if not hmac.compare_digest(grant.export_id, export_id) or not hmac.compare_digest(
        grant.user_id, user_id
    ):
        raise DownloadTokenError("download token scope mismatch")
    return grant
