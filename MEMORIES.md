# Bug-hunt memories

Tracked high-severity bugs reported by the deep bug-finding automation.
Only open or rejected PR entries; no run history.

| Bug (location / root cause) | PR | Status | Recorded |
| --- | --- | --- | --- |
| `backend/cases/materialize.py`: rematerialize overwrote known legacy power rails with catalog `None` (comment claimed null-preserving); also invented 1HP layout for identity-only revisions | https://github.com/scrimshawlife-ctrl/Patch-Hive/pull/138 | merged | 2026-07-25 |
