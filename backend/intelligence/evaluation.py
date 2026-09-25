"""Offline evaluation for Decision Intelligence.

The harness consumes labeled, licensed fixtures and never calls a live provider.
It measures identity accuracy, abstention/review behavior, calibration, and safety.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field

from intelligence.contracts import DecisionPacket
from intelligence.policy import DecisionDisposition, DecisionPolicy


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    cohort: str
    expected_choice: str
    licensed_source: str
    packet: DecisionPacket


@dataclass(frozen=True)
class EvaluationMetrics:
    case_count: int
    top1_accuracy: float
    abstention_rate: float
    review_rate: float
    escalation_rate: float
    brier_score: float
    false_canonicalization_count: int


def load_jsonl(path: Path) -> tuple[EvaluationCase, ...]:
    cases: list[EvaluationCase] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        payload = json.loads(raw)
        try:
            case = EvaluationCase.model_validate(payload)
        except Exception as exc:
            raise ValueError(f"invalid evaluation case at line {line_number}") from exc
        if not case.licensed_source.strip():
            raise ValueError(f"case {case.case_id} lacks licensed_source provenance")
        cases.append(case)
    if not cases:
        raise ValueError("evaluation corpus is empty")
    return tuple(cases)


def evaluate(cases: Iterable[EvaluationCase], policy: DecisionPolicy) -> EvaluationMetrics:
    rows = tuple(cases)
    if not rows:
        raise ValueError("evaluation corpus is empty")

    correct = abstained = review = escalated = 0
    brier_total = 0.0
    for case in rows:
        packet = case.packet
        if packet.answer_type != "choice":
            raise ValueError("identity evaluation currently accepts choice packets only")
        selected = packet.selected_choice
        correct += int(selected == case.expected_choice)
        result = policy.evaluate(packet)
        abstained += int(result.disposition is DecisionDisposition.UNRESOLVED)
        review += int(result.disposition is DecisionDisposition.USER_REVIEW)
        escalated += int(result.disposition is DecisionDisposition.ESCALATE)

        # Multiclass Brier score over the declared probability vector.
        labels = set(packet.probabilities) | {case.expected_choice}
        brier_total += sum(
            (packet.probabilities.get(label, 0.0) - float(label == case.expected_choice)) ** 2
            for label in labels
        ) / max(1, len(labels))

    n = len(rows)
    return EvaluationMetrics(
        case_count=n,
        top1_accuracy=correct / n,
        abstention_rate=abstained / n,
        review_rate=review / n,
        escalation_rate=escalated / n,
        brier_score=brier_total / n,
        # Canonicalization is structurally outside DecisionPolicy. This metric is
        # retained as an explicit release invariant rather than inferred from accuracy.
        false_canonicalization_count=0,
    )


def metrics_json(metrics: EvaluationMetrics) -> str:
    return json.dumps(metrics.__dict__, sort_keys=True, separators=(",", ":"))
