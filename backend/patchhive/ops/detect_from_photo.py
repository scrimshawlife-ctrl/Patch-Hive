"""Photo ingestion via Gemini Vision wrapper."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import List, Protocol, Optional

from patchhive.schemas import DetectedModule, EvidenceBBox
from core.discovery import register_function


@dataclass(frozen=True)
class GeminiDetection:
    label: str
    brand: Optional[str]
    hp: Optional[int]
    position: Optional[int]
    confidence: float
    bbox: List[float]


class GeminiVisionClient(Protocol):
    def detect_modules(self, image_bytes: bytes) -> List[GeminiDetection]:
        ...


def _stable_temp_id(image_id: str, label: str, index: int) -> str:
    seed = f"{image_id}:{label}:{index}".encode()
    return hashlib.sha256(seed).hexdigest()[:12]


def detect_modules_from_photo(
    image_bytes: bytes,
    image_id: str,
    client: GeminiVisionClient,
    timestamp: Optional[datetime] = None,
) -> List[DetectedModule]:
    detections = client.detect_modules(image_bytes)
    ordered = sorted(detections, key=lambda d: (d.label, d.confidence), reverse=True)
    detected_modules: List[DetectedModule] = []
    for index, detection in enumerate(ordered):
        detected_modules.append(
            DetectedModule(
                temp_id=_stable_temp_id(image_id, detection.label, index),
                label_guess=detection.label,
                brand_guess=detection.brand,
                hp_guess=detection.hp,
                position_guess=detection.position,
                confidence=detection.confidence,
                evidence=EvidenceBBox(image_id=image_id, bbox=detection.bbox),
            )
        )
    _ = timestamp
    return detected_modules


register_function(
    name="detect_modules_from_photo",
    function=detect_modules_from_photo,
    description="Run Gemini Vision detections for a rig photo.",
    input_model="image_bytes, image_id, client",
    output_model="List[DetectedModule]",
)
