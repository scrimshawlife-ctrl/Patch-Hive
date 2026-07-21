"""Consent-gated cloud vision adapter (fail-closed).

Does not call paid APIs unless:
1. ``consent_provider_processing`` is True
2. Credentials are present (``VISION_CLOUD_API_KEY`` or constructor key)
3. Explicit ``allow_live_calls=True`` (never true in CI)

Without those gates, returns NOT_COMPUTABLE quality and empty detections.
"""

from __future__ import annotations

import os
from typing import Any, Sequence

from canon.visual_contracts import (
    ClassificationCandidate,
    ConnectionCandidate,
    ImageQualityReport,
    ImageRegion,
    ResolutionStatus,
)
from evidence.vision_provider import (
    PIPELINE_VERSION,
    VisionProviderContext,
    build_provider_receipt,
)

CLOUD_PROVIDER_NAME = "cloud"
CLOUD_MODEL_DEFAULT = "unconfigured"


class ConsentRequiredError(PermissionError):
    """Raised when live cloud vision is attempted without consent."""


class CloudVisionProvider:
    """Provider-neutral cloud adapter shell.

    Live HTTP is intentionally not implemented in-repo until an approved
    vendor integration and data-retention policy are selected.
    """

    provider_name = CLOUD_PROVIDER_NAME
    model_name = CLOUD_MODEL_DEFAULT
    model_version = "0.0.0"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model_name: str | None = None,
        model_version: str = "0.0.0",
        allow_live_calls: bool = False,
        consent_provider_processing: bool = False,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("VISION_CLOUD_API_KEY", "")
        self.model_name = model_name or os.getenv("VISION_CLOUD_MODEL", CLOUD_MODEL_DEFAULT)
        self.model_version = model_version
        self.allow_live_calls = allow_live_calls
        self.consent_provider_processing = consent_provider_processing

    def _live_permitted(self) -> bool:
        return bool(self.consent_provider_processing and self.allow_live_calls and self.api_key)

    def assess_image_quality(self, ctx: VisionProviderContext) -> ImageQualityReport:
        if not self.consent_provider_processing:
            return ImageQualityReport(
                image_asset_id=ctx.image_asset_id,
                accepted=False,
                reasons=("PROVIDER_CONSENT_REQUIRED",),
                status=ResolutionStatus.NOT_COMPUTABLE,
            )
        if not self.api_key:
            return ImageQualityReport(
                image_asset_id=ctx.image_asset_id,
                accepted=False,
                reasons=("PROVIDER_CREDENTIALS_MISSING",),
                status=ResolutionStatus.NOT_COMPUTABLE,
            )
        if not self.allow_live_calls:
            return ImageQualityReport(
                image_asset_id=ctx.image_asset_id,
                accepted=False,
                reasons=("LIVE_CALLS_DISABLED",),
                status=ResolutionStatus.NOT_COMPUTABLE,
            )
        # Live quality assessment not implemented — fail closed rather than invent scores.
        return ImageQualityReport(
            image_asset_id=ctx.image_asset_id,
            accepted=False,
            reasons=("CLOUD_QUALITY_NOT_IMPLEMENTED",),
            status=ResolutionStatus.NOT_COMPUTABLE,
        )

    def detect_system_regions(self, ctx: VisionProviderContext) -> Sequence[ImageRegion]:
        return ()

    def detect_devices(self, ctx: VisionProviderContext) -> Sequence[ClassificationCandidate]:
        if not self._live_permitted():
            return ()
        raise ConsentRequiredError(
            "Live cloud device detection is not implemented; "
            "use MockDeterministicVisionProvider or RecordedFixtureVisionProvider in CI."
        )

    def classify_candidates(
        self, ctx: VisionProviderContext, candidates: Sequence[ClassificationCandidate]
    ) -> Sequence[ClassificationCandidate]:
        return tuple(candidates)

    def detect_ports(
        self, ctx: VisionProviderContext, device_candidates: Sequence[ClassificationCandidate]
    ) -> Sequence[ClassificationCandidate]:
        return ()

    def detect_controls(
        self, ctx: VisionProviderContext, device_candidates: Sequence[ClassificationCandidate]
    ) -> Sequence[ClassificationCandidate]:
        return ()

    def infer_visible_connections(
        self, ctx: VisionProviderContext, device_candidates: Sequence[ClassificationCandidate]
    ) -> Sequence[ConnectionCandidate]:
        return ()

    def provider_receipt_stub(self, ctx: VisionProviderContext, payload: Any) -> object:
        return build_provider_receipt(
            provider=self.provider_name,
            model=self.model_name,
            model_version=self.model_version,
            request_id=ctx.request_id,
            input_hash=ctx.image_asset_id,
            response_payload=payload,
            cost_metadata={"pipeline_version": PIPELINE_VERSION, "live": False},
        )


def select_vision_provider(
    *,
    consent_provider_processing: bool = False,
    prefer_cloud: bool = False,
    allow_live_calls: bool = False,
    api_key: str | None = None,
):
    """Choose mock vs consent-gated cloud adapter.

    CI and default product paths use the mock. Cloud is only selected when
    prefer_cloud is True; live calls remain fail-closed without full gates.
    """
    from evidence.vision_provider import MockDeterministicVisionProvider

    if prefer_cloud:
        return CloudVisionProvider(
            api_key=api_key,
            allow_live_calls=allow_live_calls,
            consent_provider_processing=consent_provider_processing,
        )
    return MockDeterministicVisionProvider()
