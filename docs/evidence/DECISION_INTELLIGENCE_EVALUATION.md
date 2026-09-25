# Decision Intelligence Evaluation Corpus

Status: **HARNESS READY / REAL-WORLD CORPUS NOT YET APPROVED**

The evaluator in `backend/intelligence/evaluation.py` is offline and provider-neutral.
It does not call Jev or any live model.

## Required corpus fields

Each JSONL row must contain:

- `case_id` — stable pseudonymous identifier
- `cohort` — e.g. clear-panel, glare, partial-label, clone-family, unknown
- `expected_choice` — operator-verified catalog candidate or `none_of_above`
- `licensed_source` — provenance/licensing label; blank values are rejected
- `packet` — retained DecisionPacket from the system under evaluation

Do not commit user rack photos, OCR text containing personal data, API payloads containing
secrets, or unlicensed scraped images.

## Metrics

The first gate records:

- case count
- top-1 accuracy
- abstention rate
- human-review rate
- escalation rate
- multiclass Brier score
- false-canonicalization count (architectural invariant = 0)

Top-k and cohort confusion matrices remain required before staging enablement. They need
candidate rankings/retained distributions from a sufficiently large real-world corpus.

## Threshold policy

Do **not** invent release thresholds before baseline collection.

1. Freeze a corpus SHA.
2. Run the current vision-only/candidate baseline.
3. Run the same corpus through Jev-assisted ranking.
4. Compare accuracy, calibration, abstention/review, latency, and cost.
5. Select thresholds only after reviewing the distributions and failure cases.
6. Record operator approval and corpus SHA in a retained evaluation receipt.

Until that receipt exists, `enable_decision_intelligence` remains false.
