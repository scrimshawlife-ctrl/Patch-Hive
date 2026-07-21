"""Visual system intelligence: trust boundary, inventory, and provider contracts."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from canon.contracts import PatchEdge, PatchGraph, PatchNode, PatchPort
from canon.inventory import (
    InventoryBuildError,
    build_system_capability_graph,
    build_system_inventory_revision,
    candidates_cannot_mutate_inventory,
    enforce_confirmed_inventory_constraints,
    inventory_ready_for_generation,
)
from canon.runes import detect_modules
from canon.contracts import DetectedModule, EvidenceRecord, EpistemicStatus
from canon.visual_contracts import (
    ClassificationCandidate,
    ConfirmationDecision,
    ConnectionCandidate,
    ProviderReceipt,
    ResolutionStatus,
    resolution_to_epistemic,
)
from evidence.vision_provider import (
    MockDeterministicVisionProvider,
    RecordedFixtureVisionProvider,
    VisionProviderContext,
    assert_candidates_are_untrusted,
    collect_evidence_packet,
)

NOW = datetime(2026, 7, 21, 12, 0, tzinfo=timezone.utc)


def _receipt(**overrides: object) -> ProviderReceipt:
    base = {
        "provider": "mock",
        "model": "m",
        "model_version": "1",
        "pipeline_version": "vision-evidence.v1",
        "request_id": "req-1",
        "input_hash": "a" * 64,
        "response_hash": "b" * 64,
    }
    base.update(overrides)
    return ProviderReceipt(**base)  # type: ignore[arg-type]


def _candidate(**overrides: object) -> ClassificationCandidate:
    base = {
        "candidate_id": "cand-1",
        "entity_type": "module",
        "manufacturer": "Make Noise",
        "model": "Maths",
        "confidence": 0.8,
        "confidence_method": "test",
        "classification_status": ResolutionStatus.INFERRED,
        "evidence_id": "ev-1",
        "gallery_revision_id": "mod-rev-maths",
        "provider_receipt": _receipt(),
    }
    base.update(overrides)
    return ClassificationCandidate(**base)  # type: ignore[arg-type]


def _artifact_fields() -> dict[str, object]:
    return {
        "artifact_id": "patch-1",
        "entity_id": "entity-1",
        "generator_version": "test",
        "generation_seed": 1,
        "source_run_id": "run-1",
        "source_rig_revision_id": "rig-rev-1",
        "created_at": NOW,
    }


def test_classification_candidate_cannot_self_confirm() -> None:
    with pytest.raises(ValidationError, match="USER_CONFIRMED"):
        _candidate(classification_status=ResolutionStatus.USER_CONFIRMED)


def test_obscured_connection_cannot_be_observed() -> None:
    with pytest.raises(ValidationError, match="OBSERVED"):
        ConnectionCandidate(
            connection_candidate_id="conn-1",
            source_candidate="a",
            destination_candidate="b",
            signal_type="audio",
            confidence=0.5,
            occlusion_count=1,
            status=ResolutionStatus.OBSERVED,
        )


def test_provider_detect_modules_cannot_promote_confirmed() -> None:
    def bad_provider(_photo: bytes):
        return [
            DetectedModule(
                detection_id="d1",
                label_guess="VCO",
                evidence=(
                    EvidenceRecord(
                        evidence_id="e1",
                        source_type="photo",
                        captured_at=NOW,
                        confidence=0.9,
                        status=EpistemicStatus.confirmed,
                    ),
                ),
                confidence=0.9,
                status=EpistemicStatus.confirmed,
            )
        ]

    with pytest.raises(ValueError, match="confirmed truth"):
        detect_modules(b"jpeg-bytes", bad_provider)


def test_mock_vision_provider_is_deterministic_and_untrusted() -> None:
    provider = MockDeterministicVisionProvider()
    ctx = VisionProviderContext(
        image_asset_id="img-1",
        image_bytes=b"x" * 200,
        request_id="req-1",
        seed=7,
    )
    packet_a = collect_evidence_packet(provider, ctx)
    packet_b = collect_evidence_packet(provider, ctx)
    assert packet_a == packet_b
    assert packet_a["status"] == "INFERRED"
    assert len(packet_a["devices"]) == 2
    candidates = [ClassificationCandidate.model_validate(item) for item in packet_a["devices"]]
    assert_candidates_are_untrusted(candidates)
    for candidate in candidates:
        assert candidate.classification_status is not ResolutionStatus.USER_CONFIRMED


def test_recorded_fixture_provider_rejects_confirmed_payload() -> None:
    provider = RecordedFixtureVisionProvider(
        {
            "devices": [
                {
                    "candidate_id": "c1",
                    "entity_type": "module",
                    "confidence": 0.9,
                    "confidence_method": "fixture",
                    "classification_status": "USER_CONFIRMED",
                    "evidence_id": "e1",
                }
            ]
        }
    )
    ctx = VisionProviderContext(image_asset_id="img", image_bytes=b"data", request_id="r")
    with pytest.raises(ValidationError):
        provider.detect_devices(ctx)


def test_inventory_requires_confirmation_and_is_immutable_hash_stable() -> None:
    candidate = _candidate()
    decision = ConfirmationDecision(
        confirmation_id="conf-1",
        candidate_id=candidate.candidate_id,
        status="confirm",
        resolved_status=ResolutionStatus.USER_CONFIRMED,
        confirmed_by="user-1",
        confirmed_at=NOW,
    )
    revision_a = build_system_inventory_revision(
        system_id="sys-1",
        candidates=[candidate],
        decisions=[decision],
        created_at=NOW,
        created_by="user-1",
    )
    revision_b = build_system_inventory_revision(
        system_id="sys-1",
        candidates=[candidate],
        decisions=[decision],
        created_at=NOW,
        created_by="user-1",
    )
    assert revision_a.inventory_revision_id == revision_b.inventory_revision_id
    assert revision_a.canonical_hash == revision_b.canonical_hash
    assert revision_a.canonical_hash == revision_a.computed_hash()
    assert inventory_ready_for_generation(revision_a)
    assert len(revision_a.items) == 1
    assert revision_a.items[0].resolution is ResolutionStatus.USER_CONFIRMED


def test_unconfirmed_candidates_do_not_enter_inventory() -> None:
    candidate = _candidate(candidate_id="cand-open")
    revision = build_system_inventory_revision(
        system_id="sys-1",
        candidates=[candidate],
        decisions=[],
        created_at=NOW,
    )
    assert revision.items == ()
    assert revision.unresolved_candidate_ids == ("cand-open",)
    assert not inventory_ready_for_generation(revision)


def test_confirm_without_gallery_revision_fails_closed() -> None:
    candidate = _candidate(gallery_revision_id=None)
    decision = ConfirmationDecision(
        confirmation_id="conf-1",
        candidate_id=candidate.candidate_id,
        status="confirm",
        resolved_status=ResolutionStatus.USER_CONFIRMED,
        confirmed_by="user-1",
        confirmed_at=NOW,
    )
    with pytest.raises(InventoryBuildError, match="NOT_COMPUTABLE|gallery_revision"):
        build_system_inventory_revision(
            system_id="sys-1",
            candidates=[candidate],
            decisions=[decision],
            created_at=NOW,
        )


def test_patch_constraints_reject_unconfirmed_modules() -> None:
    candidate = _candidate()
    decision = ConfirmationDecision(
        confirmation_id="conf-1",
        candidate_id=candidate.candidate_id,
        status="confirm",
        resolved_status=ResolutionStatus.USER_CONFIRMED,
        confirmed_by="user-1",
        confirmed_at=NOW,
    )
    inventory = build_system_inventory_revision(
        system_id="sys-1",
        candidates=[candidate],
        decisions=[decision],
        created_at=NOW,
    )
    out = PatchPort(
        port_id="ghost.out",
        module_instance_id="ghost",
        module_port_id="out",
        label="OUT",
        direction="output",
        signal_type="audio",
    )
    inn = PatchPort(
        port_id="ghost.in",
        module_instance_id="ghost",
        module_port_id="in",
        label="IN",
        direction="input",
        signal_type="audio",
    )
    graph = PatchGraph(
        **_artifact_fields(),
        nodes=(
            PatchNode(node_id="ghost", module_instance_id="ghost", label="Ghost", ports=(out, inn)),
        ),
        edges=(
            PatchEdge(
                edge_id="e1",
                source_port_id="ghost.out",
                target_port_id="ghost.in",
                signal_type="audio",
            ),
        ),
    )
    report = enforce_confirmed_inventory_constraints(graph=graph, inventory=inventory)
    assert report.valid is False
    codes = {issue.code for issue in report.issues}
    assert "UNCONFIRMED_MODULE" in codes


def test_patch_constraints_not_computable_without_confirmed_inventory() -> None:
    inventory = build_system_inventory_revision(
        system_id="sys-1",
        candidates=[_candidate()],
        decisions=[],
        created_at=NOW,
    )
    port = PatchPort(
        port_id="x.out",
        module_instance_id="x",
        module_port_id="out",
        label="OUT",
        direction="output",
        signal_type="cv",
    )
    graph = PatchGraph(
        **_artifact_fields(),
        nodes=(PatchNode(node_id="x", module_instance_id="x", label="X", ports=(port,)),),
        edges=(),
    )
    report = enforce_confirmed_inventory_constraints(graph=graph, inventory=inventory)
    assert report.valid is False
    assert any(issue.code == "NOT_COMPUTABLE" for issue in report.issues)


def test_capability_graph_binds_to_inventory_revision() -> None:
    candidate = _candidate()
    decision = ConfirmationDecision(
        confirmation_id="conf-1",
        candidate_id=candidate.candidate_id,
        status="confirm",
        resolved_status=ResolutionStatus.USER_CONFIRMED,
        confirmed_by="user-1",
        confirmed_at=NOW,
    )
    inventory = build_system_inventory_revision(
        system_id="sys-1",
        candidates=[candidate],
        decisions=[decision],
        created_at=NOW,
    )
    graph = build_system_capability_graph(inventory=inventory)
    assert graph.inventory_revision_id == inventory.inventory_revision_id
    assert graph.canonical_hash == graph.computed_hash()
    assert inventory.items[0].instance_id in graph.module_instance_ids()


def test_candidates_cannot_mutate_inventory_guard() -> None:
    candidates_cannot_mutate_inventory([_candidate()])
    with pytest.raises(ValidationError):
        candidates_cannot_mutate_inventory(
            [_candidate(classification_status=ResolutionStatus.USER_CONFIRMED)]
        )


def test_resolution_status_mapping() -> None:
    assert resolution_to_epistemic(ResolutionStatus.USER_CONFIRMED) is EpistemicStatus.confirmed
    assert resolution_to_epistemic(ResolutionStatus.UNKNOWN) is EpistemicStatus.missing
    assert resolution_to_epistemic(ResolutionStatus.NOT_COMPUTABLE) is EpistemicStatus.missing
