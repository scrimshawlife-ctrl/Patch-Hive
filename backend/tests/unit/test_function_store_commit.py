"""Append-only jack function registry (canon)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from canon.function_registry import (
    FunctionStatus,
    JackFunctionEntry,
    JackFunctionStore,
    SignalKind,
    confirm_and_commit_function,
)


def test_confirm_commits_append_only(tmp_path: Path) -> None:
    store = JackFunctionStore(tmp_path)
    proposed = JackFunctionEntry(
        function_id="fn.test.vendor.weirdjack",
        rev=datetime(2025, 12, 21, 0, 0, 0, tzinfo=timezone.utc),
        canonical_name="WEIRD JACK",
        description=(
            "Proposed function derived from proprietary jack label 'WEIRD JACK'. "
            "Needs confirmation."
        ),
        label_aliases=["WEIRD JACK"],
        kind_hint=SignalKind.cv,
        status=FunctionStatus.inferred,
        confidence=0.6,
        evidence_ref="test",
    )

    committed = confirm_and_commit_function(
        store,
        proposed,
        evidence_ref="confirm:test",
        confirmed_at=datetime(2025, 12, 21, 1, 0, 0, tzinfo=timezone.utc),
    )
    latest = store.get_latest("fn.test.vendor.weirdjack")
    assert latest is not None
    assert latest.status is FunctionStatus.confirmed
    assert "Confirmed by user" in latest.description
    assert committed.function_id == latest.function_id
    assert latest.evidence_ref == "confirm:test"
