# Vision Provider Strategy

Status: CANON-ALIGNED ENGINEERING SPECIFICATION

## Purpose

Define a provider-neutral, cost-controlled, privacy-aware strategy for visual evidence acquisition. Vision output is untrusted evidence and may never directly mutate canonical system state.

## Scope

PatchHive uses vision only for symbolic system understanding:

- image quality assessment
- rack and device region detection
- manufacturer and model candidate generation
- panel text extraction
- port and control candidate detection
- multi-photo reconciliation
- visible connection hypotheses

Audio capture, waveform analysis, spectral analysis, DSP, playback, synthesis, plugin hosting, and hardware activation are out of scope.

## Provider policy

The application must depend on an internal interface, not provider-specific response types.

```python
class VisionEvidenceProvider:
    def assess_image_quality(self, request): ...
    def detect_system_regions(self, request): ...
    def detect_devices(self, request): ...
    def classify_candidates(self, request): ...
    def detect_ports(self, request): ...
    def detect_controls(self, request): ...
    def infer_visible_connections(self, request): ...
```

Required implementations:

- hosted production provider
- deterministic mock provider
- recorded-fixture provider
- future local-model provider

## Initial provider posture

Gemini may be used as the initial hosted provider because it supports multimodal reasoning, multi-image analysis, structured output, OCR-like extraction, and image-region reasoning. This is an implementation choice, not a canonical dependency.

OpenAI may be added as an escalation or independent verification provider. A specialized local detector may later handle high-volume known-module detection.

## Cost-control architecture

```text
Local preprocessing
  -> image normalization and hashing
  -> one low-cost hosted analysis
  -> local Device Registry matching
  -> user confirmation
  -> deterministic reuse of confirmed inventory
```

Rules:

1. Analyze each unique image and pipeline version once.
2. Cache by image hash, provider, model version, and pipeline version.
3. Do not rerun vision when generating patches or Patch Books from an unchanged confirmed inventory.
4. Use a low-cost model for normal cases.
5. Escalate only for low confidence, registry disagreement, or explicit user request.
6. Bound image count, dimensions, response size, retries, and provider calls.
7. Enforce per-user and global budget limits.
8. Record cost metadata when the provider exposes it.
9. Development and CI must not depend on live paid calls.

## Evidence packet

Every provider response must normalize to:

```yaml
provider:
model:
model_version:
pipeline_version:
request_id:
input_hash:
response_hash:
created_at:
latency_ms:
cost_metadata:
observations:
ambiguities:
```

Each observation must include evidence reference, image region, candidate labels, provider confidence, and provenance status.

## Confidence

Provider confidence is not canonical confidence. PatchHive confidence must combine:

- provider score
- Device Registry match quality
- OCR and visible-label agreement
- geometric consistency
- multi-photo agreement
- user confirmation
- calibration against a retained evaluation set

Uncalibrated scores must be labeled as such.

## Privacy and retention

- Strip EXIF and unnecessary metadata before provider submission.
- Re-encode uploaded images into safe normalized derivatives.
- Document every third-party provider and its retention policy.
- Obtain explicit user consent before transmitting images externally.
- Do not log raw images or sensitive OCR text in general application logs.
- Support deletion of originals, derivatives, and provider-derived evidence subject to canonical retention rules.
- Production use of free tiers that permit provider training on user content is prohibited unless explicitly approved and disclosed.

## Failure behavior

Use `NOT_COMPUTABLE` when:

- no provider is configured
- budget is exhausted
- required image detail is unavailable
- provider output is malformed
- confidence is below policy threshold
- privacy consent is absent

Manual and hybrid inventory entry must remain available.

## Release gates

A hosted provider may enter production only when:

- adapter contract tests pass
- provider output is fully normalized
- retries and rate limits are bounded
- cost controls are active
- privacy policy and consent flow are implemented
- representative evaluation results are retained
- mock and fixture providers support deterministic CI
- provider failure does not block manual workflows
