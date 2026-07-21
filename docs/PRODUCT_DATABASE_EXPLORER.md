# Product Database and Explorer Specification

Status: CANON-ALIGNED P0 PRODUCT SPECIFICATION

## Purpose

The PatchHive Product Database is the public, searchable product surface backed by the canonical Device Registry and existing Module Gallery infrastructure. It must expose manufacturers, product families, modules, devices, revisions, panels, ports, controls, capabilities, documents, images, aliases, and provenance.

The Product Database is not a separate source of truth. The Device Registry remains canonical; the Product Explorer is its read-optimized product interface.

## Existing infrastructure to preserve and upgrade

PatchHive already contains:

- `patchhive/gallery/schemas_gallery_v2.py` for versioned module identity, jacks, attachments, and provenance
- `patchhive/gallery/store_v2.py` and `backend/patchhive/gallery/store.py` for gallery persistence
- `patchhive/cli/ingest_modulargrid_dataset.py` for deterministic catalog ingestion
- `backend/patchhive/gallery/match.py` for candidate matching
- module image, jack-function, and sketch enrichment operations
- admin module and gallery operations
- frontend rack and rig surfaces that already consume module records

These surfaces must be migrated or adapted rather than replaced without evidence.

## Canonical hierarchy

```text
Manufacturer
  -> ProductFamily
    -> DeviceModel
      -> DeviceRevision
        -> PanelVariant
          -> Ports
          -> Controls
          -> Capabilities
          -> Documents
          -> Images
          -> Aliases
          -> Provenance
```

A Eurorack module is a device subtype. The database must also support semi-modular instruments, desktop synthesizers, pedals, rack processors, controllers, utilities, and unknown/custom devices.

## Product navigation

Add a first-class `Products` or `Explore` entry to global navigation.

Required routes:

- `/products`
- `/products/manufacturers`
- `/products/manufacturers/{manufacturer_slug}`
- `/products/{device_id}`
- `/products/{device_id}/revisions/{revision_id}`
- `/products/categories/{category_slug}`
- `/products/search`

The existing Module Gallery remains available as an administrative and evidence-resolution surface. Public browsing must not expose internal mutation controls.

## Product Explorer home

The home view must support:

- all manufacturers
- all products and modules
- product families
- functional categories
- formats
- recently added records
- recently updated records
- discontinued products
- records needing evidence or enrichment, admin only
- database coverage and freshness indicators

Do not claim that the database contains every brand or module until a retained coverage receipt proves it.

## Manufacturer page

Each manufacturer page must include:

- canonical name and aliases
- official website and source links
- active, discontinued, acquired, or unknown status
- product families
- current products
- discontinued products
- total record count
- records by format and category
- evidence completeness summary
- latest registry update

## Product page

Every product page should expose, when supported by evidence:

- manufacturer
- canonical product name
- aliases and regional names
- family
- product type and format
- release state
- release and discontinuation dates
- front and rear panel images
- HP, depth, dimensions, and weight
- power requirements
- inputs, outputs, and bidirectional ports
- controls, switches, displays, and indicators
- signal classes and connector types
- voltage, level, impedance, and normalled behavior
- functional capabilities
- firmware and hardware revisions
- official manuals and specification sheets
- known limitations and unresolved properties
- compatible PatchHive patches
- systems using the product, aggregated and privacy-safe
- provenance for every technical field

Unknown fields remain visibly unknown. Missing data must never be rendered as zero, false, unsupported, or safe.

## Search and filtering

Required filters:

- manufacturer
- product family
- product type
- format
- category and capability
- HP and physical dimensions
- power requirements
- active or discontinued status
- input and output signal classes
- connector type
- revision
- evidence completeness

Search must support exact names, aliases, OCR-confusable names, common shorthand, and semantic capability queries.

Examples:

```text
Make Noise Maths
quad VCA under 10 HP
stereo filter
generative clock source
manufacturer:Mutable Instruments status:discontinued
```

## Read API

Provide versioned, cursor-paginated read contracts:

- `GET /v1/products`
- `GET /v1/products/{device_id}`
- `GET /v1/products/{device_id}/revisions`
- `GET /v1/manufacturers`
- `GET /v1/manufacturers/{manufacturer_id}`
- `GET /v1/product-categories`
- `GET /v1/product-search`
- `GET /v1/registry/coverage`

Responses must expose canonical IDs, schema version, record version, evidence completeness, and last-reviewed timestamps.

## Administrative workflow

Reuse and upgrade the existing Module Gallery and admin operations to support:

- create and edit manufacturer candidates
- import product datasets
- resolve duplicate manufacturers and products
- attach official sources
- create immutable revisions
- upload panel images and manuals
- enrich ports, controls, and capabilities
- approve or reject inferred fields
- merge aliases without breaking references
- deprecate or tombstone records
- inspect downstream usage before mutation
- publish deterministic registry snapshots

All changes require audit events. Referenced revisions cannot be hard-deleted.

## Import strategy

The database may ingest from:

1. official manufacturer product pages and manuals
2. licensed or permission-compatible third-party catalogs
3. existing ModularGrid-compatible datasets where terms permit
4. user-confirmed images and corrections
5. curated internal records

Every import must produce:

- source identity and license basis
- source version or retrieval date
- input hash
- normalization version
- imported, updated, skipped, rejected, and ambiguous counts
- duplicate-resolution report
- deterministic manifest hash

No scraper or external dataset may silently become canonical authority.

## Coverage model

Track coverage by manufacturer, product type, format, category, and evidence field.

Required states:

- `CATALOGED`
- `IDENTITY_CONFIRMED`
- `PHYSICAL_CONFIRMED`
- `PORTS_CONFIRMED`
- `CONTROLS_CONFIRMED`
- `CAPABILITIES_CONFIRMED`
- `DOCUMENTATION_CONFIRMED`
- `VISION_READY`
- `PATCH_READY`
- `COMPLETE_FOR_CURRENT_SCHEMA`

Completeness is schema-relative and versioned. A record may be patch-ready without being fully complete.

## Vision integration

```text
Photo evidence
  -> visual candidates
  -> Product Database retrieval
  -> deterministic candidate ranking
  -> user confirmation
  -> immutable system inventory revision
```

The vision provider cannot create canonical products directly. Unknown products enter a review queue and may be manually added only with retained evidence.

## Patch integration

Product records provide the capabilities and constraints used by patch generation and validation. Product pages should list compatible generated patches, but patch generation must consume immutable Device Registry revisions rather than mutable display records.

## Performance and indexing

Start with PostgreSQL full-text and indexed relational filters. Add a dedicated search engine only when measured catalog scale or query latency requires it.

Required indexes include:

- canonical and normalized manufacturer name
- canonical product name
- aliases
- device type and format
- category and capability
- release state
- physical dimensions
- evidence completeness

## Accessibility

Target WCAG 2.2 AA. Tables and dense product records require semantic headings, keyboard-accessible filters, non-color completeness indicators, and text alternatives for panel diagrams.

## P0 acceptance criteria

- users can browse all imported manufacturers and products
- manufacturer and product detail pages use canonical IDs
- filters and alias-aware search work deterministically
- current Module Gallery data is available through the explorer without duplication
- provenance and unknown states are visible
- admin enrichment preserves revision history and audit events
- registry coverage is measurable and never overstated
- vision candidate resolution uses the same canonical records
- patch generation references immutable registry revisions

## Out of scope

- audio playback or analysis
- DSP or synthesis emulation
- marketplace purchasing
- unreviewed community claims as canonical facts
- claims of complete worldwide catalog coverage without evidence
