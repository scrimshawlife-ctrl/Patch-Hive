"""Legacy ``patch_hive`` compatibility package.

This package is not part of the canonical backend distribution. It remains in the repository
for explicit compatibility review only and is quarantined from production-like runtimes.
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
        if os.environ.get(key, "").strip().lower() in _PRODUCTION_VALUES:
            return True
    return False


if _runtime_is_production() and not _truthy(os.environ.get(_ALLOW_ENV)):
    raise ImportError(
        "Refusing to import legacy patch_hive package in a production-like runtime from "
        f"{Path(__file__).resolve()}. Set {_ALLOW_ENV}=1 only for an explicit compatibility job."
    )
