"""Append-only jack function registry (CANON_MVP).

Supersedes historical ``patchhive.registry.function_store`` for product tests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from canon.contracts import canonical_json, canonical_sha256


class FunctionStatus(str, Enum):
    inferred = "inferred"
    confirmed = "confirmed"
    rejected = "rejected"


class SignalKind(str, Enum):
    audio = "audio"
    cv = "cv"
    gate = "gate"
    trigger = "trigger"
    clock = "clock"
    unknown = "unknown"


class JackFunctionEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    function_id: str
    rev: datetime
    canonical_name: str
    description: str
    label_aliases: list[str] = Field(default_factory=list)
    kind_hint: SignalKind = SignalKind.unknown
    status: FunctionStatus = FunctionStatus.inferred
    confidence: float = Field(ge=0, le=1, default=0.5)
    evidence_ref: str | None = None

    def to_storage_dict(self) -> dict[str, Any]:
        return json.loads(canonical_json(self.model_dump(mode="json")))


@dataclass(frozen=True)
class RegistryPaths:
    root: Path

    def fn_dir(self, function_id: str) -> Path:
        safe = function_id.replace("/", "_")
        return self.root / safe

    def rev_path(self, function_id: str, rev: datetime) -> Path:
        iso = rev.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        return self.fn_dir(function_id) / f"{iso}.json"


class JackFunctionStore:
    """Append-only revisions for jack function entries."""

    def __init__(self, root: str | Path) -> None:
        self.paths = RegistryPaths(root=Path(root))
        self.paths.root.mkdir(parents=True, exist_ok=True)

    def list_revisions(self, function_id: str) -> list[Path]:
        d = self.paths.fn_dir(function_id)
        if not d.exists():
            return []
        return sorted(p for p in d.iterdir() if p.suffix == ".json")

    def get_latest(self, function_id: str) -> JackFunctionEntry | None:
        revs = self.list_revisions(function_id)
        if not revs:
            return None
        raw = json.loads(revs[-1].read_text(encoding="utf-8"))
        return JackFunctionEntry.model_validate(raw)

    def append_revision(self, entry: JackFunctionEntry) -> Path:
        path = self.paths.rev_path(entry.function_id, entry.rev)
        if path.exists():
            raise ValueError("Function rev collision. Provide unique rev timestamp.")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        payload = canonical_json(entry.model_dump(mode="json"))
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(path)
        return path


def confirm_and_commit_function(
    store: JackFunctionStore,
    proposed: JackFunctionEntry,
    *,
    evidence_ref: str,
    confidence: float = 0.98,
    confirmed_at: datetime | None = None,
) -> JackFunctionEntry:
    """Write a confirmed append-only revision (user-initiated only)."""
    stamped = confirmed_at or datetime.now(timezone.utc)
    description = proposed.description.replace("Needs confirmation.", "Confirmed by user.")
    confirmed = proposed.model_copy(
        update={
            "rev": stamped,
            "description": description,
            "status": FunctionStatus.confirmed,
            "confidence": confidence,
            "evidence_ref": evidence_ref,
        }
    )
    store.append_revision(confirmed)
    return confirmed


def function_entry_hash(entry: JackFunctionEntry) -> str:
    return canonical_sha256(entry.model_dump(mode="json"))
