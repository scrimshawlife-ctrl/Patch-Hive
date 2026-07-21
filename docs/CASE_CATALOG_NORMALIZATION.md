# PatchHive Case Catalog Normalization

**Status:** implementation contract  
**Baseline:** `feat(cases): research case catalog ingest (50 cases) (#97)`  
**Tracking:** #98

## Decision

The existing `cases` table remains the backward-compatible rack attachment surface during migration. It is not the long-term canonical case catalog because it combines identity, geometry, power, provenance, and format-specific capacity in one record and assumes HP-oriented semantics.

The canonical case knowledge graph is split into stable product identity plus revisioned technical records. Unknown fields remain `NULL`. No importer may infer electrical or physical values from adjacent products, photographs, marketing names, or format conventions.

## Entities

### `case_catalog`

Lightweight discovery identity.

| Field | Type | Rule |
|---|---|---|
| `id` | integer PK | internal identity |
| `slug` | varchar(240) unique | normalized manufacturer + model |
| `manufacturer` | varchar(120) | indexed |
| `model` | varchar(200) | indexed |
| `format_family` | varchar(40) | controlled vocabulary |
| `production_status` | varchar(24) | `available`, `discontinued`, `upcoming`, `unknown` |
| `official_url` | varchar(800) nullable | manufacturer product surface |
| `image_url` | varchar(800) nullable | non-canonical presentation asset |
| `legacy_case_id` | integer nullable unique | bridge to existing `cases.id` |
| timestamps | timezone-aware datetime | create/update |

### `case_revisions`

Revision-specific enclosure and capacity facts.

| Field | Type | Rule |
|---|---|---|
| `id` | integer PK | |
| `case_catalog_id` | FK | cascade delete |
| `revision_key` | varchar(120) | manufacturer revision, generation, or `default` |
| `revision_label` | varchar(200) nullable | human-readable |
| `capacity_value` | numeric nullable | never implicitly HP |
| `capacity_unit` | varchar(40) | controlled vocabulary |
| `row_count` | integer nullable | |
| `depth_min_mm` | numeric nullable | minimum explicitly usable zone |
| `depth_max_mm` | numeric nullable | maximum published internal depth |
| `depth_notes` | text nullable | zone/discrepancy detail |
| `width_mm`, `height_mm`, `depth_mm` | numeric nullable | external dimensions |
| `weight_kg` | numeric nullable | |
| `materials` | JSON nullable | normalized list plus published text |
| `mounting_type` | varchar(40) nullable | threaded strip, sliding nut, rack ear, proprietary |
| `portable` | boolean nullable | unknown is distinct from false |
| `lid_type` | varchar(40) nullable | none, removable, hinged, unknown |
| `closes_patched` | boolean nullable | |
| `stand_modes` | JSON nullable | desktop, upright, angled, linked, rackmount |
| `published_spec` | JSON nullable | lossless source representation |
| `verification_status` | varchar(24) | `verified`, `incomplete`, `conflict` |
| `valid_from`, `valid_to` | date nullable | revision history |

Unique constraint: `(case_catalog_id, revision_key)`.

### `case_rows`

Row-level geometry where widths, formats, or depth zones differ.

| Field | Type | Rule |
|---|---|---|
| `case_revision_id` | FK | |
| `row_index` | integer | zero-based |
| `row_format` | varchar(40) | e.g. `eurorack_3u`, `intellijel_1u` |
| `capacity_value` | numeric nullable | |
| `capacity_unit` | varchar(40) | |
| `usable_depth_mm` | numeric nullable | conservative fit depth |
| `depth_notes` | text nullable | |

Unique constraint: `(case_revision_id, row_index)`.

### `case_power_systems`

One revision may have no power system, one integrated system, or multiple documented zones.

| Field | Type | Rule |
|---|---|---|
| `case_revision_id` | FK unique | null relation means undocumented/unpowered is represented explicitly |
| `powered` | boolean nullable | unknown is distinct from false |
| `supply_type` | varchar(40) nullable | integrated, external brick, passive, proprietary |
| `input_spec` | varchar(240) nullable | retain published wording |
| `busboard_type` | varchar(80) nullable | |
| `connector_count` | integer nullable | |
| `power_12v_ma` | integer nullable | rail capacity |
| `power_neg12v_ma` | integer nullable | rail capacity |
| `power_5v_ma` | integer nullable | rail capacity |
| `other_rails` | JSON nullable | proprietary rails |
| `distribution_zones` | JSON nullable | zone-specific limits |
| `protections` | JSON nullable | reverse polarity, short circuit, filtering |
| `power_notes` | text nullable | discrepancy detail |

A record with `powered=false` must have all rail values `NULL`, not zero.

### `case_features`

Normalized feature flags with optional detail.

Primary feature keys include:

- `integrated_midi`
- `integrated_cv`
- `integrated_audio_io`
- `integrated_usb`
- `utility_row`
- `cv_bus`
- `rack_ears`
- `link_system`
- `expansion_supported`
- `removable_lid`
- `close_patched_lid`

Unique constraint: `(case_revision_id, feature_key)`.

### `case_prices`

Append-only price observations. Prices are not product identity.

Required dimensions: source/vendor, region, currency, amount, price kind (`msrp`, `street`, `used`), stock status, captured timestamp, source URL.

### `case_sources`

Record- or field-level provenance.

Required fields:

- source type: `official_manual`, `official_product`, `retailer`, `community`, `internal_import`
- URL/reference
- captured timestamp
- confidence: `high`, `medium`, `low`
- field paths covered
- content hash when locally captured
- discrepancy note

Authority order: official manual > official product page > reputable retailer > community. Lower-authority evidence may flag a conflict but cannot silently overwrite a higher-authority value.

## Controlled vocabularies

### Format families

- `eurorack`
- `buchla_200`
- `serge_4u`
- `mu_5u`
- `frac`
- `other`

1U compatibility belongs at row level (`intellijel_1u`, `pulplogic_1u`) and must not be treated as interchangeable.

### Capacity units

- `hp`
- `mu_space`
- `buchla_panel`
- `serge_panel`
- `frac_width`
- `custom`

## Legacy bridge

The 50 imported rows in `fixtures/cases_research_2026.json` remain valid evidence and seed material. Migration performs the following deterministic projection:

1. Create or locate `case_catalog` by normalized `(brand, name)`.
2. Create revision key `research-2026-default` unless source evidence names a generation.
3. Convert `meta.capacity_unit` to the controlled vocabulary.
4. Preserve existing `total_hp` as `capacity_value`; it is only HP when the normalized unit is `hp`.
5. Convert `hp_per_row` into `case_rows` with row format inferred only when explicitly represented by fixture metadata. Otherwise row format remains `other` and receives a warning.
6. Copy power rails without filling missing values.
7. Copy `manufacturer_url`, source, source reference, and notes into `case_sources`.
8. Link the new catalog identity to `legacy_case_id`.

The existing `cases` API continues to operate until rack foreign keys migrate to `case_revision_id`. No destructive table rewrite occurs in the first migration.

## Import receipt

Every import emits a canonical JSON receipt containing:

```json
{
  "schema_version": "patchhive.case-import-receipt.v1",
  "input_sha256": "...",
  "source_manifest_sha256": "...",
  "started_at": "...",
  "completed_at": "...",
  "dry_run": true,
  "counts": {
    "input": 0,
    "inserted": 0,
    "updated": 0,
    "unchanged": 0,
    "rejected": 0,
    "warnings": 0
  },
  "rejections": [],
  "warnings": []
}
```

Receipts must be deterministic except for timestamps. A normalized row hash controls idempotent upsert behavior.

## Compatibility result contract

Physical and electrical checks return a status, never a bare boolean:

- `verified`: all required facts are sourced and compatible
- `incomplete`: compatibility cannot be established because one or more facts are unknown
- `conflict`: documented facts disagree or the requested configuration exceeds a known limit

Each result includes machine-readable reasons and source references.

## Delivery sequence

1. Add SQLAlchemy models and Alembic migration without modifying `cases`.
2. Add Pydantic ingest/read schemas and controlled vocabularies.
3. Implement projection of the existing 50-case fixture into normalized tables.
4. Add idempotence, unknown-field, non-Eurorack, and downgrade tests.
5. Add read-only catalog endpoints.
6. Add compatibility service.
7. Migrate Rack Builder to revision identity.
8. Retire direct writes to the legacy `cases` table only after parity evidence.

## Acceptance gates

- migration upgrade and downgrade succeed on SQLite test DB and PostgreSQL staging
- all 50 research records project without fabricated values
- repeated import produces zero inserts and zero updates
- non-Eurorack capacities never acquire HP semantics
- `powered=false` never produces zero-valued rails
- row-level depth is used before revision-level maximum depth
- every conflict/incomplete result exposes reasons
- existing rack and case endpoints remain backward compatible during transition
