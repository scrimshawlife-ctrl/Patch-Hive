from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, Optional


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


@dataclass
class JobState:
    run_id: str
    status: JobStatus
    stage: str
    progress: float  # 0..1
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "run_id": self.run_id,
            "status": self.status.value,
            "stage": self.stage,
            "progress": self.progress,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }

    @staticmethod
    def from_dict(d: Dict) -> "JobState":
        return JobState(
            run_id=d["run_id"],
            status=JobStatus(d["status"]),
            stage=d.get("stage", "unknown"),
            progress=float(d.get("progress", 0.0)),
            started_at=d.get("started_at"),
            finished_at=d.get("finished_at"),
            error=d.get("error"),
        )


class JobStore:
    """
    store_root/jobs/<run_id>.json
    """
    def __init__(self, store_root: str):
        self.root = Path(store_root) / "jobs"
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, run_id: str) -> Path:
        return self.root / f"{run_id}.json"

    def write(self, state: JobState) -> None:
        self.path(state.run_id).write_text(
            json.dumps(state.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def read(self, run_id: str) -> Optional[JobState]:
        p = self.path(run_id)
        if not p.exists():
            return None
        return JobState.from_dict(json.loads(p.read_text(encoding="utf-8")))
