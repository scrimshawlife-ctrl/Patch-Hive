from datetime import datetime, timezone

from intelligence.contracts import DecisionPacket
from intelligence.evaluation import EvaluationCase, evaluate
from intelligence.policy import DecisionPolicy, PolicyThresholds


def _packet(choice: str, probabilities: dict[str, float], confidence: float):
    return DecisionPacket(
        decision_id=f"d-{choice}",
        request_id=f"r-{choice}",
        provider="fixture",
        provider_version="eval-v1",
        evidence_hash="h",
        answer_type="choice",
        selected_choice=choice,
        probabilities=probabilities,
        confidence=confidence,
        candidate_set_hash="set",
        created_at=datetime.now(timezone.utc),
    )


def test_evaluation_reports_accuracy_calibration_and_abstention() -> None:
    policy = DecisionPolicy(
        PolicyThresholds(
            policy_version="eval-v1",
            auto_propose_at=0.9,
            user_review_at=0.65,
            probability_margin=0.1,
        )
    )
    cases = (
        EvaluationCase(
            case_id="a",
            cohort="clear-panel",
            expected_choice="mod-a",
            licensed_source="synthetic-fixture",
            packet=_packet("mod-a", {"mod-a": 0.95, "none_of_above": 0.05}, 0.95),
        ),
        EvaluationCase(
            case_id="b",
            cohort="unknown",
            expected_choice="none_of_above",
            licensed_source="synthetic-fixture",
            packet=_packet("none_of_above", {"mod-b": 0.1, "none_of_above": 0.9}, 0.9),
        ),
    )
    metrics = evaluate(cases, policy)
    assert metrics.case_count == 2
    assert metrics.top1_accuracy == 1.0
    assert metrics.abstention_rate == 0.5
    assert metrics.false_canonicalization_count == 0
    assert 0 <= metrics.brier_score <= 1
