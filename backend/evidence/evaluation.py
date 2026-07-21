"""Vision evaluation metrics over a versioned fixture dataset.

Production accuracy is **NOT_COMPUTABLE** without a representative, licensed
dataset. This module:

1. Loads labeled fixture packets from ``fixtures/vision_eval/``
2. Runs a deterministic provider (mock/fixture) against each sample
3. Computes precision/recall/top-k when ground truth is present
4. Returns ``NOT_COMPUTABLE`` for metrics that cannot be scored

Never claims production readiness from synthetic fixture scores alone.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from evidence.vision_provider import (
    MockDeterministicVisionProvider,
    RecordedFixtureVisionProvider,
    VisionEvidenceProvider,
    VisionProviderContext,
    collect_evidence_packet,
)

METRIC_NOT_COMPUTABLE = "NOT_COMPUTABLE"
EVAL_DATASET_VERSION = "vision-eval.v1"


@dataclass(frozen=True)
class EvalSample:
    sample_id: str
    image_bytes: bytes
    # Ground-truth module labels (normalized lowercase strings)
    true_labels: tuple[str, ...] = ()
    true_manufacturers: tuple[str, ...] = ()
    notes: str | None = None
    # Optional pre-recorded provider packet for fixture provider path
    recorded_packet: dict[str, Any] | None = None


@dataclass
class MetricResult:
    name: str
    value: float | None
    status: str  # OK | NOT_COMPUTABLE | INSUFFICIENT_LABELS
    detail: str = ""


@dataclass
class EvaluationReport:
    dataset_version: str
    sample_count: int
    provider: str
    model: str
    metrics: list[MetricResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_version": self.dataset_version,
            "sample_count": self.sample_count,
            "provider": self.provider,
            "model": self.model,
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "status": m.status,
                    "detail": m.detail,
                }
                for m in self.metrics
            ],
            "notes": list(self.notes),
            "production_accuracy_claim": METRIC_NOT_COMPUTABLE,
        }


def _normalize_label(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


def _predicted_labels(packet: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for device in packet.get("devices") or []:
        model = device.get("model") or device.get("label_guess")
        manufacturer = device.get("manufacturer") or device.get("brand_guess")
        if model:
            labels.append(_normalize_label(f"{manufacturer or ''} {model}".strip()))
    return labels


def _precision_recall(true_set: set[str], pred_set: set[str]) -> tuple[float | None, float | None]:
    if not true_set and not pred_set:
        return 1.0, 1.0
    if not true_set:
        return None, None
    if not pred_set:
        return 0.0, 0.0
    tp = len(true_set & pred_set)
    precision = tp / len(pred_set) if pred_set else 0.0
    recall = tp / len(true_set) if true_set else 0.0
    return precision, recall


def load_eval_dataset(dataset_dir: Path) -> list[EvalSample]:
    """Load samples from a directory containing manifest.json + sample folders."""

    manifest_path = dataset_dir / "manifest.json"
    if not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    samples: list[EvalSample] = []
    for entry in manifest.get("samples") or []:
        sample_id = str(entry["sample_id"])
        sample_dir = dataset_dir / sample_id
        image_path = sample_dir / entry.get("image", "image.bin")
        labels_path = sample_dir / entry.get("labels", "labels.json")
        image_bytes = image_path.read_bytes() if image_path.exists() else b"x" * 200
        labels: dict[str, Any] = {}
        if labels_path.exists():
            labels = json.loads(labels_path.read_text(encoding="utf-8"))
        recorded = None
        recorded_path = sample_dir / "recorded_packet.json"
        if recorded_path.exists():
            recorded = json.loads(recorded_path.read_text(encoding="utf-8"))
        samples.append(
            EvalSample(
                sample_id=sample_id,
                image_bytes=image_bytes,
                true_labels=tuple(_normalize_label(x) for x in (labels.get("modules") or []) if x),
                true_manufacturers=tuple(
                    _normalize_label(x) for x in (labels.get("manufacturers") or []) if x
                ),
                notes=labels.get("notes"),
                recorded_packet=recorded,
            )
        )
    return samples


def evaluate_provider(
    samples: Sequence[EvalSample],
    *,
    provider: VisionEvidenceProvider | None = None,
    use_recorded_when_available: bool = True,
) -> EvaluationReport:
    """Run evaluation and compute available metrics."""

    default_provider = provider or MockDeterministicVisionProvider()
    report = EvaluationReport(
        dataset_version=EVAL_DATASET_VERSION,
        sample_count=len(samples),
        provider=default_provider.provider_name,
        model=default_provider.model_name,
        notes=[
            "Synthetic/fixture scores are not production accuracy.",
            "Representative licensed datasets required before production claims.",
        ],
    )

    if not samples:
        report.metrics.append(
            MetricResult(
                name="module_detection_precision",
                value=None,
                status=METRIC_NOT_COMPUTABLE,
                detail="empty evaluation dataset",
            )
        )
        report.metrics.append(
            MetricResult(
                name="module_detection_recall",
                value=None,
                status=METRIC_NOT_COMPUTABLE,
                detail="empty evaluation dataset",
            )
        )
        return report

    precisions: list[float] = []
    recalls: list[float] = []
    labeled = 0
    for sample in samples:
        active: VisionEvidenceProvider = default_provider
        if use_recorded_when_available and sample.recorded_packet is not None:
            active = RecordedFixtureVisionProvider(sample.recorded_packet)
        ctx = VisionProviderContext(
            image_asset_id=sample.sample_id,
            image_bytes=sample.image_bytes,
            request_id=f"eval-{sample.sample_id}",
        )
        packet = collect_evidence_packet(active, ctx)
        true_set = set(sample.true_labels)
        if not true_set:
            continue
        labeled += 1
        pred_set = set(_predicted_labels(packet))
        # Loose match: any true label substring of a prediction or vice versa
        matched_true: set[str] = set()
        matched_pred: set[str] = set()
        for t in true_set:
            for p in pred_set:
                if t in p or p in t:
                    matched_true.add(t)
                    matched_pred.add(p)
        p, r = _precision_recall(matched_true or true_set, matched_pred or pred_set)
        # Prefer strict set metrics when exact normalize matches exist
        p_strict, r_strict = _precision_recall(true_set, pred_set)
        if p_strict is not None:
            precisions.append(p_strict)
            recalls.append(r_strict if r_strict is not None else 0.0)
        elif p is not None:
            precisions.append(p)
            recalls.append(r if r is not None else 0.0)

    def _avg(values: list[float], name: str) -> MetricResult:
        if not values:
            return MetricResult(
                name=name,
                value=None,
                status=METRIC_NOT_COMPUTABLE,
                detail=f"labeled_samples={labeled}",
            )
        return MetricResult(
            name=name,
            value=sum(values) / len(values),
            status="OK",
            detail=f"labeled_samples={labeled}",
        )

    report.metrics.append(_avg(precisions, "module_detection_precision"))
    report.metrics.append(_avg(recalls, "module_detection_recall"))
    report.metrics.append(
        MetricResult(
            name="manufacturer_accuracy",
            value=None,
            status=METRIC_NOT_COMPUTABLE,
            detail="manufacturer ground truth incomplete in synthetic set",
        )
    )
    report.metrics.append(
        MetricResult(
            name="exact_model_accuracy",
            value=None,
            status=METRIC_NOT_COMPUTABLE,
            detail="requires representative production dataset",
        )
    )
    report.metrics.append(
        MetricResult(
            name="unknown_rejection_accuracy",
            value=None,
            status=METRIC_NOT_COMPUTABLE,
            detail="requires negative-class evaluation set",
        )
    )
    report.metrics.append(
        MetricResult(
            name="confidence_calibration_error",
            value=None,
            status=METRIC_NOT_COMPUTABLE,
            detail="requires calibration dataset",
        )
    )
    return report


def default_fixture_dataset_path() -> Path:
    """Repo fixtures path relative to backend package location."""
    return Path(__file__).resolve().parents[2] / "fixtures" / "vision_eval"
