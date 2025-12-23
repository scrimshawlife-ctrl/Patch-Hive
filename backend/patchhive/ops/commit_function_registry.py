from __future__ import annotations

from datetime import datetime, timezone

from patchhive.registry.function_store import JackFunctionStore
from patchhive.schemas import FieldMeta, FieldStatus, JackFunctionEntry, Provenance, ProvenanceType


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def confirm_and_commit_function(
    store: JackFunctionStore,
    proposed: JackFunctionEntry,
    *,
    evidence_ref: str,
    confidence: float = 0.98,
) -> JackFunctionEntry:
    """
    Takes a proposed JackFunctionEntry and writes a CONFIRMED append-only revision.
    """
    meta = FieldMeta(
        provenance=[
            Provenance(
                type=ProvenanceType.manual,
                timestamp=_now_utc(),
                evidence_ref=evidence_ref,
                method="confirm_and_commit_function",
            )
        ],
        confidence=confidence,
        status=FieldStatus.confirmed,
    )

    confirmed = proposed.model_copy(
        update={
            "rev": _now_utc(),
            "description": proposed.description.replace(
                "Needs confirmation.", "Confirmed by user."
            ),
            "provenance": list(meta.provenance),
            "meta": meta,
        }
    )
    store.append_revision(confirmed)
    return confirmed
