"""Multi-photo candidate reconciliation (VSI workstream 6).

Fuses device candidates observed across multiple image evidence packets for
one rack/system. Conflicting claims stay explicit; nothing is auto-confirmed.

Rules:
- Match candidates across photos by normalized manufacturer+model key.
- Aggregate confidences (mean of observations); track supporting image ids.
- Conflicts (same key with material model disagreement) are reported, not forced.
- Output remains untrusted until ConfirmationDecision creates inventory.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Sequence

from canon.visual_contracts import ClassificationCandidate, ResolutionStatus


def _norm(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


def entity_key(candidate: ClassificationCandidate | dict[str, Any]) -> str:
    if isinstance(candidate, ClassificationCandidate):
        mfr = candidate.manufacturer
        model = candidate.model
        entity = candidate.entity_type
        cand_id = candidate.candidate_id
    else:
        mfr = candidate.get("manufacturer")
        model = candidate.get("model")
        entity = candidate.get("entity_type")
        cand_id = candidate.get("candidate_id")
    base = f"{_norm(mfr)}|{_norm(model)}|{_norm(str(entity or 'module'))}"
    if base.strip("|") == "" or base == "||module":
        return f"id:{cand_id}"
    return base


@dataclass
class Observation:
    candidate_id: str
    image_asset_id: str | None
    confidence: float
    raw: dict[str, Any]


@dataclass
class FusedEntity:
    fuse_id: str
    entity_key: str
    manufacturer: str | None
    model: str | None
    entity_type: str
    observations: list[Observation] = field(default_factory=list)
    supporting_image_ids: list[str] = field(default_factory=list)
    mean_confidence: float = 0.0
    max_confidence: float = 0.0
    conflict: bool = False
    conflict_notes: list[str] = field(default_factory=list)
    classification_status: str = ResolutionStatus.INFERRED.value

    def to_dict(self) -> dict[str, Any]:
        return {
            "fuse_id": self.fuse_id,
            "entity_key": self.entity_key,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "entity_type": self.entity_type,
            "observation_count": len(self.observations),
            "supporting_image_ids": list(self.supporting_image_ids),
            "mean_confidence": self.mean_confidence,
            "max_confidence": self.max_confidence,
            "conflict": self.conflict,
            "conflict_notes": list(self.conflict_notes),
            "classification_status": self.classification_status,
            "representative_candidate_id": (
                self.observations[0].candidate_id if self.observations else None
            ),
        }


@dataclass
class ReconciliationReport:
    image_asset_ids: list[str]
    fused_entities: list[FusedEntity]
    unmatched_candidate_ids: list[str]
    conflict_count: int
    status: str  # OK | INSUFFICIENT_IMAGES | EMPTY

    def to_dict(self) -> dict[str, Any]:
        return {
            "image_asset_ids": list(self.image_asset_ids),
            "image_count": len(self.image_asset_ids),
            "fused_entities": [e.to_dict() for e in self.fused_entities],
            "unmatched_candidate_ids": list(self.unmatched_candidate_ids),
            "conflict_count": self.conflict_count,
            "status": self.status,
            "note": (
                "Fused evidence remains untrusted until user confirmation; "
                "conflicts are never auto-resolved."
            ),
        }


def reconcile_candidate_observations(
    candidates: Sequence[dict[str, Any]],
    *,
    min_images_for_multi: int = 2,
) -> ReconciliationReport:
    """Reconcile flat candidate dicts (as returned by evidence list helpers)."""

    image_ids = sorted(
        {str(c.get("image_asset_id")) for c in candidates if c.get("image_asset_id")}
    )
    if not candidates:
        return ReconciliationReport(
            image_asset_ids=image_ids,
            fused_entities=[],
            unmatched_candidate_ids=[],
            conflict_count=0,
            status="EMPTY",
        )
    if len(image_ids) < min_images_for_multi:
        # Still fuse (single-photo pass-through) but mark insufficient for multi metrics.
        status = "INSUFFICIENT_IMAGES"
    else:
        status = "OK"

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cand in candidates:
        try:
            parsed = ClassificationCandidate.model_validate(
                cand.get("_raw") or {k: v for k, v in cand.items() if k != "_raw"}
            )
        except Exception:
            continue
        key = entity_key(parsed)
        groups[key].append(cand)

    fused: list[FusedEntity] = []
    unmatched: list[str] = []
    conflicts = 0
    for idx, (key, members) in enumerate(sorted(groups.items(), key=lambda x: x[0])):
        confidences = [float(m.get("confidence") or 0.0) for m in members]
        images = sorted({str(m.get("image_asset_id")) for m in members if m.get("image_asset_id")})
        models = {_norm(m.get("model")) for m in members if m.get("model")}
        mfrs = {_norm(m.get("manufacturer")) for m in members if m.get("manufacturer")}
        conflict_notes: list[str] = []
        conflict = False
        if len(models) > 1:
            conflict = True
            conflict_notes.append(f"model_disagreement:{sorted(models)}")
        if len(mfrs) > 1:
            conflict = True
            conflict_notes.append(f"manufacturer_disagreement:{sorted(mfrs)}")
        if conflict:
            conflicts += 1

        # Prefer highest-confidence observation as representative labels
        best = max(members, key=lambda m: float(m.get("confidence") or 0.0))
        observations = [
            Observation(
                candidate_id=str(m.get("candidate_id")),
                image_asset_id=m.get("image_asset_id"),
                confidence=float(m.get("confidence") or 0.0),
                raw={k: v for k, v in m.items() if k != "_raw"},
            )
            for m in members
        ]
        fused.append(
            FusedEntity(
                fuse_id=f"fuse-{idx:04d}-{key[:24]}",
                entity_key=key,
                manufacturer=best.get("manufacturer"),
                model=best.get("model"),
                entity_type=str(best.get("entity_type") or "module"),
                observations=observations,
                supporting_image_ids=images,
                mean_confidence=(sum(confidences) / len(confidences)) if confidences else 0.0,
                max_confidence=max(confidences) if confidences else 0.0,
                conflict=conflict,
                conflict_notes=conflict_notes,
                classification_status=(
                    ResolutionStatus.INFERRED.value
                    if not conflict
                    else ResolutionStatus.UNKNOWN.value
                ),
            )
        )

    # Sort: more support and higher confidence first; conflicts last among equals
    fused.sort(
        key=lambda e: (
            e.conflict,
            -len(e.supporting_image_ids),
            -e.mean_confidence,
            e.entity_key,
        )
    )
    return ReconciliationReport(
        image_asset_ids=image_ids,
        fused_entities=fused,
        unmatched_candidate_ids=unmatched,
        conflict_count=conflicts,
        status=status,
    )
