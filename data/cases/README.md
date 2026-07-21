# PatchHive Modular Case Dataset

This directory contains provenance-backed modular synthesizer case records for the normalized case catalog.

## Authority

The JSON files here are import inputs, not unreviewed canonical truth. Canonical database state is produced only after:

1. schema validation;
2. source-policy validation;
3. deterministic normalization;
4. revision and alias reconciliation;
5. import receipt generation;
6. review of conflicts and blocked records.

Unknown values must be omitted or set to `null`. Do not encode unknown values as `0`, `false`, empty strings, or inferred defaults.

## File layout

```text
data/cases/
  README.md
  schema.example.json
  seed-v1.json                 # research-candidate seed (50 cases)
  seed-v1.sources.json         # source and licensing manifest
  seed-v1.coverage.json        # field coverage statistics
  receipts/
    seed-v1.dry-run.json       # dry-run receipt bound to seed SHA-256
```

Regenerate the seed from the research fixture:

```bash
python3 scripts/build_case_catalog_seed.py
```

## Required identity fields

Each case record requires:

- `manufacturer`
- `model`
- `format_family`

Supported format families:

- `eurorack`
- `intellijel_1u`
- `pulplogic_1u`
- `buchla_200`
- `serge_4u`
- `mu_5u`
- `frac`
- `other`

Capacity is always paired with a unit. Supported units are `hp`, `mu_space`, `buchla_panel`, `serge_panel`, `frac_width`, and `custom`.

## Source policy

Every published technical field should have a source entry with a field path and a policy packet. Minimum policy fields for reviewed records:

- `access_basis`
- `license_status`
- `evidence_status`
- `review_state`
- `observed_at`
- `retrieved_at`
- `content_hash`
- `normalizer_version`

Allowed access bases:

- `official_publication`
- `authorized_feed`
- `licensed_dataset`
- `user_authorized_export`
- `manual_research`
- `user_upload`
- `provider_inference`
- `unknown`

Records with `unknown` access basis, unresolved licensing, conflicted compatibility evidence, or missing source hashes may be retained for research but must not be represented as verified canonical data.

## Import

```bash
cd backend
python -m integrations.case_catalog_populator \
  --input ../data/cases/seed-v1.json \
  --dry-run \
  --receipt ../data/cases/receipts/seed-v1.dry-run.json
```

A production import must use the exact file whose SHA-256 appears in the reviewed dry-run receipt.

## Read API

Normalized catalog endpoints (additive; legacy `/api/cases/{id}` remains):

```text
GET /api/cases/catalog
GET /api/cases/catalog/manufacturers
GET /api/cases/catalog/formats
GET /api/cases/catalog/stats
GET /api/cases/catalog/{slug}
GET /api/cases/catalog/{slug}/revisions
```

Filters on list include manufacturer, format_family, capacity range/unit, row count,
powered, depth, rail headroom, portable/lid/stand, production_status, feature_key, and `q`.
