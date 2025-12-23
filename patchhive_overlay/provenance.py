"""
Provenance utilities for Patch-Hive overlay.

Provides deterministic run IDs, payload hashing, and environment fingerprinting
for complete traceability in the Abraxas/AAL ecosystem.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _canon(obj: Any) -> str:
    """Canonical JSON serialization for deterministic hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s: str) -> str:
    """SHA-256 hash of a string, returned as hex digest."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def utc_iso() -> str:
    """Current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def try_git_head() -> Optional[str]:
    """Try to get current git HEAD commit hash."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return None


def env_fingerprint() -> Dict[str, Any]:
    """Capture environment details for provenance."""
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "git_head": try_git_head(),
        "cwd": os.getcwd(),
    }


@dataclass(frozen=True)
class Provenance:
    """Immutable provenance record for overlay operations."""

    run_id: str
    ts_utc: str
    payload_hash: str
    env: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "run_id": self.run_id,
            "ts_utc": self.ts_utc,
            "payload_hash": self.payload_hash,
            "env": self.env,
        }


def make_provenance(
    overlay: str,
    capability: str,
    payload: Dict[str, Any],
    seed: Optional[str] = None,
) -> Provenance:
    """
    Create provenance record for an overlay capability invocation.

    Args:
        overlay: Name of the overlay service (e.g., "patchhive")
        capability: Capability being invoked (e.g., "patchhive.generate_patch")
        payload: Input payload dictionary
        seed: Optional seed for deterministic run_id (uses timestamp if None)

    Returns:
        Provenance record with deterministic run_id and environment metadata
    """
    ts = utc_iso()
    payload_hash = sha256_hex(_canon(payload))
    salt = seed if seed is not None else ts
    run_id = sha256_hex(
        _canon(
            {
                "overlay": overlay,
                "capability": capability,
                "payload_hash": payload_hash,
                "salt": salt,
            }
        )
    )
    return Provenance(run_id=run_id, ts_utc=ts, payload_hash=payload_hash, env=env_fingerprint())
