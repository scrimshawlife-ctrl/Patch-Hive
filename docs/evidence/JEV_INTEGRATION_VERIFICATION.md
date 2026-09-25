# Jev integration contract verification

Verified: 2026-09-25

Status: VERIFIED_PUBLIC_CONTRACT / LIVE_CREDENTIAL_CALL_NOT_RUN

## Verified public contract

PatchHive's Jev adapter targets the documented TypeSafe System One HTTP interface:

- evaluation route: POST /v1/systemone;
- authentication: Bearer credential;
- request body: model, state, questions;
- question primitives: choice, score, noul;
- multiple named questions may be evaluated in one request;
- GET /v1/models is available for authenticated model discovery;
- an Idempotency-Key header is documented and should be used for controlled calls.

The existing PatchHive adapter's endpoint shape and three primitive mappings are therefore aligned with the current public interface.

## Model-version rule

`jev-latest` is a moving alias. It is acceptable for development discovery, but it MUST NOT be used to generate a retained baseline, calibration result, threshold decision, or release receipt.

T061d/T062 evaluation MUST:

1. discover/verify the available model identifier;
2. select a pinned Jev release;
3. record that exact identifier in the evaluation receipt;
4. keep corpus SHA and policy version fixed during comparison.

Changing the model invalidates comparison against an earlier retained Jev measurement unless a new evaluation receipt is generated.

## Idempotency rule

Controlled provider calls SHOULD send the DecisionRequest idempotency identity through the provider's documented Idempotency-Key header in addition to PatchHive's local request identity. This is an integration-hardening item before T070.

## Evidence boundary

Public documentation verification proves protocol compatibility only. It does not prove:

- account authorization;
- live response compatibility for the configured credential;
- latency/cost for PatchHive workloads;
- calibration on PatchHive's corpus;
- production readiness.

Those remain empirical gates.

## T070 preflight

Before controlled staging enablement:

- [ ] representative corpus admitted and frozen;
- [ ] pinned Jev model selected;
- [ ] live credential call succeeds against the documented contract;
- [ ] response validates into provider-neutral DecisionPacket;
- [ ] timeout/error path fails closed;
- [ ] idempotency behavior checked;
- [ ] latency and cost recorded;
- [ ] baseline/Jev receipt retained;
- [ ] operator threshold approval recorded;
- [ ] feature remains disabled in production.
