from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from patchhive.ops.commit_function_registry import confirm_and_commit_function
from patchhive.registry.function_store import JackFunctionStore
from patchhive.schemas import (
    FieldMeta,
    FieldStatus,
    JackFunctionEntry,
    Provenance,
    ProvenanceType,
    SignalKind,
)


def test_confirm_commits_append_only(tmp_path: Path) -> None:
    store = JackFunctionStore(tmp_path)

    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.derived,
                timestamp=datetime(2025, 12, 21, tzinfo=timezone.utc),
                evidence_ref="test",
            )
        ],
        confidence=0.6,
        status=FieldStatus.inferred,
    )

    proposed = JackFunctionEntry(
        function_id="fn.test.vendor.weirdjack",
        rev=datetime(2025, 12, 21, 0, 0, 0, tzinfo=timezone.utc),
        canonical_name="WEIRD JACK",
        description=(
            "Proposed function derived from proprietary jack label 'WEIRD JACK'. Needs confirmation."
        ),
        label_aliases=["WEIRD JACK"],
        kind_hint=SignalKind.cv,
        provenance=list(meta.provenance),
        meta=meta,
    )

    committed = confirm_and_commit_function(store, proposed, evidence_ref="confirm:test")
    latest = store.get_latest("fn.test.vendor.weirdjack")
    assert latest is not None
    assert latest.meta.status.value == "confirmed"
    assert "Confirmed by user" in latest.description
    assert committed.function_id == latest.function_id
