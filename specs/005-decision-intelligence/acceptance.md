# Acceptance

## Contract
- [ ] Provider-specific response types cannot enter canon package contracts.
- [ ] Candidate result outside server-authored set is rejected.
- [ ] Packet hashes and idempotency are deterministic.
- [ ] Unsupported schema/policy versions fail closed.

## Authority
- [ ] No DecisionPacket can directly create/update SystemInventoryRevision.
- [ ] Provider failure cannot transition to CONFIRMED/CANONICALIZED.
- [ ] Low confidence cannot be converted to a fabricated negative fact.
- [ ] Existing user confirmation remains required for probabilistic identity/capability proposals.

## Evaluation
- [ ] Versioned labeled corpus exists with provenance/licensing notes.
- [ ] Baseline and Jev results are retained.
- [ ] Top-1/top-k, calibration, review/abstention, escalation, latency/cost are reported.
- [ ] False canonicalization = 0.
- [ ] Thresholds are selected after observing baseline; no invented target is treated as evidence.

## Operations
- [ ] Jev flag defaults OFF.
- [ ] Provider timeout/retry caps tested.
- [ ] Provider outage leaves canonical generation safe.
- [ ] Rollback disables Jev without schema/data loss.

## Documentation
- [ ] README/current state/roadmap link the feature spec.
- [ ] Architecture marks decision intelligence as evidence-side, not canonical authority.
- [ ] Legacy/historical docs are not silently promoted to authority.
