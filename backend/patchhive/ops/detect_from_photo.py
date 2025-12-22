"""Gemini detection wrapper for module identification from photos."""

from __future__ import annotations

from typing import Protocol, Sequence

from patchhive.schemas import DetectedModule


class GeminiClient(Protocol):
    """Protocol for Gemini detection clients."""

    def detect_modules_from_photo(self, photo_bytes: bytes) -> Sequence[DetectedModule]:
        """Return detected modules from a photo."""
        raise NotImplementedError


class GeminiFixtureClient:
    """Deterministic fixture client for tests."""

    def __init__(self, fixtures: Sequence[DetectedModule]) -> None:
        self._fixtures = list(fixtures)

    def detect_modules_from_photo(self, photo_bytes: bytes) -> Sequence[DetectedModule]:
        return list(self._fixtures)


def detect_modules_from_photo_v1(
    photo_bytes: bytes,
    client: GeminiClient,
) -> list[DetectedModule]:
    """Detect modules using a Gemini-compatible client."""
    return list(client.detect_modules_from_photo(photo_bytes))
