"""Path helpers for monorepo-aware unit tests.

Works when:
- running on host from repo (`.../Patch-Hive/backend/tests/...`)
- running in backend container with `./backend` mounted at `/app` and
  `./frontend` mounted at `/frontend` (see docker-compose.yml).
"""

from __future__ import annotations

from pathlib import Path


def monorepo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        frontend = parent / "frontend" / "src"
        backend_marker = (parent / "backend").is_dir() or (parent / "main.py").exists()
        if frontend.is_dir() and backend_marker:
            return parent
    if Path("/frontend/src").is_dir():
        return Path("/")
    raise FileNotFoundError(
        "Cannot locate monorepo root containing frontend/src "
        "(host checkout or docker-compose frontend mount at /frontend)."
    )


def frontend_src() -> Path:
    root = monorepo_root()
    if root == Path("/"):
        return Path("/frontend/src")
    return root / "frontend" / "src"
