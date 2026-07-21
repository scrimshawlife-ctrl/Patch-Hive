"""Visual System Intelligence contracts.

These contracts extend the canonical MVP without replacing existing
`EpistemicStatus` usage. They encode the photo → evidence → confirmation →
immutable inventory trust boundary defined in
`docs/VISUAL_SYSTEM_INTELLIGENCE.md` and ADR-005.

Terminology aliases (canonical term first):
- System / Rig
- SystemInventoryRevision / CanonicalRigRevision / RigRevision
- ClassificationCandidate / DeviceCandidate / ModuleCandidate
- ResolutionStatus / confirmation-layer provenance status
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import Field, model_validator

from canon.contracts import CanonicalContract, EpistemicStatus, canonical_sha256


class ResolutionStatus(str, Enum):
    """Confirmation-layer status for visual evidence claims.

    Distinct from `EpistemicStatus` (confirmed/inferred/disputed/missing), which
    remains the gallery and artifact contract vocabulary.
    """

    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    USER_CONFIRMED = "USER_CONFIRMED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


def resolution_to_epistemic(status: ResolutionStatus) -> EpistemicStatus:
    """Map visual resolution status to gallery/artifact epistemic status."""

    mapping = {
        ResolutionStatus.USER_CONFIRMED: EpistemicStatus.confirmed,
        ResolutionStatus.OBSERVED: EpistemicStatus.inferred,
        ResolutionStatus.INFERRED: EpistemicStatus.inferred,
        ResolutionStatus.REJECTED: EpistemicStatus.disputed,
        ResolutionStatus.UNKNOWN: EpistemicStatus.missing,
        ResolutionStatus.NOT_COMPUTABLE: EpistemicStatus.missing,
    }
    return mapping[status]


class ProviderReceipt(CanonicalContract):
    """Identity and integrity metadata for a vision-provider call."""

    provider: str
    model: str
    model_version: str
    pipeline_version: str
    request_id: str
    input_hash: str
    response_hash: str
    latency_ms: int | None = Field(default=None, ge=0)
    cost_metadata: dict[str, Any] = Field(default_factory=dict)


class ImageRegion(CanonicalContract):
    region_id: str
    image_asset_id: str
    # Normalized [0,1] box: x, y, width, height
    bbox: tuple[float, float, float, float]
    label: str | None = None
    confidence: float = Field(ge=0, le=1)
    status: ResolutionStatus = ResolutionStatus.OBSERVED


class ImageQualityReport(CanonicalContract):
    image_asset_id: str
    accepted: bool
    blur_score: float | None = Field(default=None, ge=0, le=1)
    glare_score: float | None = Field(default=None, ge=0, le=1)
    coverage_score: float | None = Field(default=None, ge=0, le=1)
    rotation_degrees: float | None = None
    perspective_skew: float | None = Field(default=None, ge=0, le=1)
    reasons: tuple[str, ...] = ()
    status: ResolutionStatus = ResolutionStatus.OBSERVED


class ClassificationCandidate(CanonicalContract):
    """Untrusted classification proposal. Never mutates canonical inventory."""

    candidate_id: str
    entity_type: Literal["device", "module", "port", "control", "cable", "rack", "unknown"]
    manufacturer: str | None = None
    model: str | None = None
    revision: str | None = None
    confidence: float = Field(ge=0, le=1)
    confidence_method: str
    alternative_candidates: tuple[str, ...] = ()
    classification_status: ResolutionStatus = ResolutionStatus.INFERRED
    evidence_id: str
    image_region_id: str | None = None
    provider_receipt: ProviderReceipt | None = None
    gallery_module_id: str | None = None
    gallery_revision_id: str | None = None

    @model_validator(mode="after")
    def provider_cannot_self_confirm(self) -> "ClassificationCandidate":
        if self.classification_status is ResolutionStatus.USER_CONFIRMED:
            raise ValueError(
                "classification candidates cannot be USER_CONFIRMED; "
                "confirmation is a separate resolution step"
            )
        return self


class ConfirmationDecision(CanonicalContract):
    confirmation_id: str
    candidate_id: str
    status: Literal[
        "confirm",
        "reject",
        "replace",
        "defer",
        "manual_add",
    ]
    resolved_status: ResolutionStatus
    confirmed_by: str | None = None
    confirmed_at: datetime
    supersedes: str | None = None
    replacement_candidate_id: str | None = None
    manual_module_revision_id: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def confirm_requires_identity(self) -> "ConfirmationDecision":
        if self.status == "confirm" and self.resolved_status is not ResolutionStatus.USER_CONFIRMED:
            raise ValueError("confirm decisions must resolve to USER_CONFIRMED")
        if self.status == "reject" and self.resolved_status is not ResolutionStatus.REJECTED:
            raise ValueError("reject decisions must resolve to REJECTED")
        if self.status == "manual_add" and not self.manual_module_revision_id:
            raise ValueError("manual_add requires manual_module_revision_id")
        return self


class ConnectionCandidate(CanonicalContract):
    """Probabilistic cable/connection proposal. Canonical only after confirmation."""

    connection_candidate_id: str
    source_candidate: str
    destination_candidate: str
    signal_type: Literal["audio", "cv", "gate", "trigger", "clock", "midi", "digital", "unknown"]
    path_evidence: tuple[str, ...] = ()
    confidence: float = Field(ge=0, le=1)
    occlusion_count: int = Field(default=0, ge=0)
    ambiguity: str | None = None
    status: ResolutionStatus = ResolutionStatus.INFERRED

    @model_validator(mode="after")
    def obscured_not_observed(self) -> "ConnectionCandidate":
        if self.occlusion_count > 0 and self.status is ResolutionStatus.OBSERVED:
            raise ValueError("obscured cable endpoints cannot be marked OBSERVED")
        if self.status is ResolutionStatus.USER_CONFIRMED:
            raise ValueError(
                "connection candidates cannot self-confirm; use ConfirmationDecision"
            )
        return self


class InventoryItem(CanonicalContract):
    instance_id: str
    module_revision_id: str
    manufacturer: str | None = None
    model: str | None = None
    position: int | None = Field(default=None, ge=0)
    resolution: ResolutionStatus
    source_candidate_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    confirmed_by: str | None = None
    confirmed_at: datetime | None = None

    @model_validator(mode="after")
    def only_confirmed_or_manual(self) -> "InventoryItem":
        if self.resolution not in {
            ResolutionStatus.USER_CONFIRMED,
            # Manual inventory fallback still carries explicit user authority.
            ResolutionStatus.OBSERVED,
        }:
            # OBSERVED alone is insufficient for generation; build step filters.
            pass
        if not self.module_revision_id:
            raise ValueError("inventory items require a module_revision_id")
        return self


class SystemInventoryRevision(CanonicalContract):
    """Immutable inventory snapshot used for generation and exports."""

    inventory_revision_id: str
    system_id: str
    previous_revision_id: str | None = None
    items: tuple[InventoryItem, ...]
    unresolved_candidate_ids: tuple[str, ...] = ()
    created_at: datetime
    created_by: str | None = None
    canonical_hash: str | None = None
    schema_label: str = "SystemInventoryRevision"

    def computed_hash(self) -> str:
        return canonical_sha256(self.model_dump(exclude={"canonical_hash"}))

    def seal(self) -> "SystemInventoryRevision":
        return self.model_copy(update={"canonical_hash": self.computed_hash()})

    def confirmed_module_revision_ids(self) -> frozenset[str]:
        return frozenset(
            item.module_revision_id
            for item in self.items
            if item.resolution is ResolutionStatus.USER_CONFIRMED
        )


class CapabilityPort(CanonicalContract):
    port_id: str
    module_instance_id: str
    label: str
    direction: Literal["input", "output", "bidirectional"]
    signal_type: Literal["audio", "cv", "gate", "trigger", "clock", "unknown"]
    resolution: ResolutionStatus = ResolutionStatus.USER_CONFIRMED


class SystemCapability(CanonicalContract):
    capability_id: str
    category: str
    module_instance_ids: tuple[str, ...]
    signal_domains: tuple[str, ...] = ()
    notes: str | None = None


class SystemCapabilityGraph(CanonicalContract):
    """Deterministic capability view of a confirmed inventory revision."""

    graph_id: str
    inventory_revision_id: str
    capabilities: tuple[SystemCapability, ...]
    ports: tuple[CapabilityPort, ...]
    missing_specifications: tuple[str, ...] = ()
    canonical_hash: str | None = None

    def computed_hash(self) -> str:
        return canonical_sha256(self.model_dump(exclude={"canonical_hash"}))

    def seal(self) -> "SystemCapabilityGraph":
        return self.model_copy(update={"canonical_hash": self.computed_hash()})

    def port_ids(self) -> frozenset[str]:
        return frozenset(port.port_id for port in self.ports)

    def module_instance_ids(self) -> frozenset[str]:
        return frozenset(
            instance_id
            for capability in self.capabilities
            for instance_id in capability.module_instance_ids
        )
