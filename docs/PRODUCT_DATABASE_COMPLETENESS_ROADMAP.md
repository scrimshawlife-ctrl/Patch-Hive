# Product Database Completeness Roadmap

Status: EXECUTION-READY ENGINEERING ROADMAP

## Objective

Turn the existing Module Gallery, module-library files, ModularGrid ingestion path, enrichment operations, and Device Registry specification into a complete, user-visible Product Database covering all brands and products that PatchHive can lawfully and accurately source.

`All brands and modules` is a target, not a present-tense claim. Coverage remains `NOT_COMPUTABLE` until measured against a defined reference universe and exact registry snapshot.

## Baseline infrastructure

Observed repository surfaces to preserve:

- versioned gallery schema and store
- deterministic module keys and IDs
- ModularGrid-compatible dataset ingestion
- generated panel sketches
- module image and jack enrichment operations
- gallery candidate matching
- frontend rack-builder and rig-detail consumers
- admin module/gallery operations

## Work package PDB-01 — Inventory and reconcile existing stores

Priority: P0

- enumerate all file-backed module-library and gallery records
- compare canonical IDs, `module_key`, and content-addressed revision IDs
- identify duplicate and conflicting records
- produce source, manufacturer, module, and completeness counts
- classify legacy, active, and transitional stores
- define one canonical read model and compatibility adapters

Acceptance:

- exact-SHA inventory receipt
- no silent record loss
- duplicate-resolution queue produced
- authoritative and compatibility surfaces documented

## Work package PDB-02 — Registry schema upgrade

Priority: P0

Upgrade current module-only records toward:

```text
Manufacturer -> ProductFamily -> DeviceModel -> DeviceRevision -> PanelVariant
```

Add normalized records for:

- manufacturers
- families
- models
- revisions
- ports
- controls
- capabilities
- documents
- images
- aliases
- field evidence
- review state

Preserve compatibility with current `ModuleGalleryRevision` consumers until migration is verified.

Acceptance:

- versioned schema
- migration and rollback plan
- stable IDs
- unknown-state preservation
- deterministic snapshot export

## Work package PDB-03 — Product read API

Priority: P0

Implement paginated endpoints for products, manufacturers, categories, search, revisions, and coverage. Responses must be schema-versioned and evidence-aware.

Acceptance:

- authorization rules documented
- cursor pagination tested
- alias-aware exact search
- deterministic ordering
- coverage endpoint returns snapshot-bound counts

## Work package PDB-04 — Public Product Explorer

Priority: P0

Build:

- explorer landing page
- all-manufacturers directory
- manufacturer detail page
- product detail page
- category and format views
- searchable/filterable product results
- explicit unknown and evidence states

Acceptance:

- accessible keyboard workflow
- responsive layouts
- loading, empty, partial, stale, and error states
- no admin controls exposed publicly
- existing gallery records visible without duplication

## Work package PDB-05 — Admin registry workbench

Priority: P0

Upgrade existing admin/gallery tools for manufacturer management, revision creation, source attachment, duplicate merges, aliases, enrichment, review queues, tombstones, and snapshot publication.

Acceptance:

- all mutations audited
- referenced revisions immutable
- merge impact preview
- no hard deletion of referenced records

## Work package PDB-06 — Source acquisition and licensing

Priority: P0

For each source, retain:

- owner
- license or permission basis
- acquisition method
- fields permitted for storage and display
- image/manual redistribution rules
- retrieval/version date
- source hash

Do not ingest or republish data without a documented legal basis.

Acceptance:

- source registry exists
- unsupported sources rejected
- provenance attached at field or inherited-record level

## Work package PDB-07 — Catalog expansion campaign

Priority: P1

Execute manufacturer-by-manufacturer waves:

1. highest-usage Eurorack manufacturers
2. long-tail and discontinued Eurorack manufacturers
3. semi-modular and desktop instruments
4. pedals, rack processors, and controllers
5. unknown/custom device workflow

Each wave produces a retained coverage receipt and review queue.

## Work package PDB-08 — Enrichment

Priority: P1

Enrich identity-only records with physical data, power, ports, controls, capabilities, manuals, images, revisions, and aliases.

Prioritize:

1. identity confirmation
2. dimensions and power
3. ports and signal classes
4. capabilities required by patch generation
5. control and panel geometry
6. supplemental descriptions

## Work package PDB-09 — Search and semantic retrieval

Priority: P1

Start with PostgreSQL indexes and full-text search. Add embeddings only for semantic capability retrieval, with source text and embedding-model version retained.

## Work package PDB-10 — Vision readiness

Priority: P1

A product is vision-ready only when it has sufficient panel evidence, aliases, geometry, and candidate-discriminating features. Track top-k recognition performance by manufacturer and module family.

## Completeness metrics

Every registry snapshot reports:

- manufacturer count
- model count
- revision count
- active/discontinued split
- records by type and format
- identity-confirmed percentage
- patch-ready percentage
- vision-ready percentage
- field coverage for dimensions, power, ports, controls, capabilities, images, and manuals
- duplicate and ambiguity counts
- source/licensing coverage

## Release gates

The public explorer may launch before global completeness only when:

- coverage is disclosed accurately
- search and filters operate on all imported records
- unknown fields remain explicit
- provenance is retained
- patch and vision workflows share canonical IDs
- no unsupported completeness claim is displayed

A claim such as `complete Eurorack database` requires a named reference universe, comparison method, date, exact snapshot ID, and retained exception list.
