"""Image quality gates and vision provider adapter tests."""

import io

from PIL import Image

from evidence.images import (
    SignatureImageScanner,
    assess_local_image_quality,
    prepare_image_evidence,
)
from evidence.vision_provider import (
    MockDeterministicVisionProvider,
    VisionProviderContext,
    collect_evidence_packet,
)


def _jpeg(width: int = 128, height: int = 96) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (width, height), (10, 20, 30)).save(output, format="JPEG")
    return output.getvalue()


def test_local_quality_accepts_normalized_image() -> None:
    prepared = prepare_image_evidence(
        _jpeg(), declared_media_type="image/jpeg", scanner=SignatureImageScanner()
    )
    assessment = assess_local_image_quality(prepared)
    assert assessment.accepted is True
    assert assessment.reasons == ()
    assert assessment.content_sha256 == prepared.sha256


def test_local_quality_rejects_tiny_image() -> None:
    prepared = prepare_image_evidence(
        _jpeg(width=16, height=16),
        declared_media_type="image/jpeg",
        scanner=SignatureImageScanner(),
    )
    assessment = assess_local_image_quality(prepared, min_dimension=64)
    assert assessment.accepted is False
    assert "IMAGE_DIMENSIONS_TOO_SMALL" in assessment.reasons


def test_mock_provider_rejects_tiny_bytes() -> None:
    provider = MockDeterministicVisionProvider(min_bytes_for_accept=100)
    ctx = VisionProviderContext(
        image_asset_id="img-tiny",
        image_bytes=b"short",
        request_id="req",
    )
    packet = collect_evidence_packet(provider, ctx)
    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["devices"] == []
