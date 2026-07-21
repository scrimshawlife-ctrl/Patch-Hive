"""Evaluation harness and consent-gated cloud provider tests."""

from pathlib import Path

from evidence.cloud_provider import CloudVisionProvider, select_vision_provider
from evidence.evaluation import (
    METRIC_NOT_COMPUTABLE,
    evaluate_provider,
    load_eval_dataset,
)
from evidence.vision_provider import MockDeterministicVisionProvider, VisionProviderContext

FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "fixtures" / "vision_eval"


def test_load_and_evaluate_fixture_dataset() -> None:
    samples = load_eval_dataset(FIXTURE_ROOT)
    assert len(samples) >= 1
    report = evaluate_provider(samples, provider=MockDeterministicVisionProvider())
    assert report.sample_count >= 1
    assert report.to_dict()["production_accuracy_claim"] == METRIC_NOT_COMPUTABLE
    names = {m.name: m for m in report.metrics}
    assert "module_detection_precision" in names
    assert "exact_model_accuracy" in names
    assert names["exact_model_accuracy"].status == METRIC_NOT_COMPUTABLE
    # Synthetic labeled sample should yield a numeric precision when mock emits devices
    precision = names["module_detection_precision"]
    assert precision.status in {"OK", METRIC_NOT_COMPUTABLE}


def test_empty_dataset_is_not_computable() -> None:
    report = evaluate_provider([])
    assert report.sample_count == 0
    assert all(m.status == METRIC_NOT_COMPUTABLE for m in report.metrics)


def test_cloud_provider_requires_consent() -> None:
    provider = CloudVisionProvider(
        consent_provider_processing=False, allow_live_calls=True, api_key="x"
    )
    ctx = VisionProviderContext(image_asset_id="i", image_bytes=b"x" * 200, request_id="r")
    quality = provider.assess_image_quality(ctx)
    assert quality.accepted is False
    assert "PROVIDER_CONSENT_REQUIRED" in quality.reasons
    assert provider.detect_devices(ctx) == ()


def test_cloud_provider_fail_closed_without_live_flag() -> None:
    provider = CloudVisionProvider(
        consent_provider_processing=True, allow_live_calls=False, api_key="secret"
    )
    ctx = VisionProviderContext(image_asset_id="i", image_bytes=b"x" * 200, request_id="r")
    quality = provider.assess_image_quality(ctx)
    assert quality.accepted is False
    assert "LIVE_CALLS_DISABLED" in quality.reasons


def test_select_vision_provider_defaults_to_mock() -> None:
    provider = select_vision_provider(prefer_cloud=False)
    assert isinstance(provider, MockDeterministicVisionProvider)
    cloud = select_vision_provider(prefer_cloud=True, consent_provider_processing=True)
    assert isinstance(cloud, CloudVisionProvider)
