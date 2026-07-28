"""Legacy top-level PatchHive package retained for compatibility.

The canonical importable backend package lives at ``backend/patchhive`` and is the only
``patchhive`` package included by ``backend/pyproject.toml``. This top-level tree remains in
the repository for historical tests and migration review, but production runtimes must not
accidentally import it from the repository root.
"""

from __future__ import annotations

import os
from pathlib import Path

_ALLOW_ENV = "PATCHHIVE_ALLOW_LEGACY_IMPORTS"
_PRODUCTION_VALUES = {"prod", "production", "staging"}


def _truthy(value: str | None) -> bool:
    return value is not None and value.strip().lower() in {"1", "true", "yes", "on"}


def _runtime_is_production() -> bool:
    for key in ("PATCHHIVE_ENV", "APP_ENV", "ENV", "ENVIRONMENT"):
        value = os.environ.get(key, "").strip().lower()
        if value in _PRODUCTION_VALUES:
            return True
    return False


def _enforce_legacy_quarantine() -> None:
    if _truthy(os.environ.get(_ALLOW_ENV)) or not _runtime_is_production():
        return
    package_path = Path(__file__).resolve()
    raise ImportError(
        "Refusing to import legacy top-level patchhive package in a production-like "
        f"runtime from {package_path}. Use backend/patchhive via the backend package "
        f"path, or set {_ALLOW_ENV}=1 only for an explicit compatibility job."
    )


_enforce_legacy_quarantine()

"""PatchHive deterministic rig metrics and canonical schemas."""
