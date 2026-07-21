# Device Registry Specification

Status: CANON-ALIGNED ENGINEERING SPECIFICATION

## Purpose

The Device Registry is the resolving authority for manufacturer, model, revision, physical layout, ports, controls, capabilities, and known constraints. Vision providers propose candidates; the registry and user confirmation resolve them.

## Canonical entities

```text
Manufacturer
  -> DeviceFamily
    -> DeviceModel
      -> DeviceRevision
        -> PanelVariant
          -> Ports
          -> Controls
          -> Capabilities
          -> Evidence
```

A Eurorack module is a device subtype. The registry must also support semi-modular instruments, desktop synthesizers, pedals, rack processors, controllers, utilities, and unknown/custom devices.

## Required records

### Manufacturer

- manufacturer_id
- canonical_name
- aliases
- website
- provenance
- status

### DeviceModel

- device_id
- manufacturer_id
- canonical_name
- aliases
- product_family
- device_type
- format
- dimensions
- release_state
- official_sources
- provenance

### DeviceRevision

- revision_id
- device_id
- revision_label
- panel_variant
- firmware_constraints
- physical_changes
- functional_changes
- valid_from
- valid_to
- provenance

### Port

- port_id
- revision_id
- canonical_label
- aliases
- direction
- signal_class
- connector_type
- channel_count
- voltage_or_level_domain
- impedance_or_electrical_data
- normalled_connection
- location_geometry
- evidence_status

### Control

- control_id
- revision_id
- canonical_label
- control_type
- range
- units
- discrete_values
- default_or_neutral_position
- location_geometry
- related_capabilities
- evidence_status

### Capability

- capability_id
- canonical_type
- parameters
- constraints
- required_ports
- required_controls
- provenance

## Status vocabulary

Every technical field must carry or inherit one of:

- `OBSERVED`
- `INFERRED`
- `USER_CONFIRMED`
- `REGISTRY_CONFIRMED`
- `REJECTED`
- `UNKNOWN`
- `NOT_COMPUTABLE`

Unknown technical properties must remain unknown. No adapter may fabricate voltage, direction, power, firmware, port behavior, or safety information.

## Identity and aliases

Device identity must be stable and independent of display names. Aliases may include:

- manufacturer spelling variants
- abbreviated model names
- regional names
- panel labels
- legacy names
- community shorthand
- OCR-confusable forms

Aliases never replace canonical identity and require provenance.

## Candidate resolution

```text
Visual observation
  -> normalized visible text and features
  -> registry retrieval
  -> ranked candidates
  -> deterministic scoring
  -> user confirmation when ambiguous
  -> immutable inventory revision
```

Candidate scoring may use:

- manufacturer text agreement
- model text agreement
- panel geometry
- dimensions
- control count and arrangement
- port count and arrangement
- logo match
- neighboring-module constraints
- multi-photo agreement

The scoring function must be versioned and testable.

## Revision handling

A device revision is immutable once referenced by a system inventory revision or generated run. Corrections create a new registry revision and preserve supersession links.

Hard deletion is prohibited for referenced records. Use deprecation, tombstoning, or alias/merge mappings.

## Capability graph integration

The registry supplies validated capability facts to the System Capability Graph. Patch generation may use only capabilities available in the confirmed inventory revision.

A missing capability is not equivalent to an absent capability. The graph must distinguish:

- confirmed available
- confirmed unavailable
- unresolved
- not applicable

## Ingestion sources

Permitted sources include:

- manufacturer manuals
- official product pages
- official MIDI or SysEx documentation
- user-confirmed panel images
- curated datasets
- licensed third-party catalogs

Community sources may provide candidate evidence but must not silently override official or user-confirmed data.

## Registry administration

Required operations:

- create manufacturer and device records
- add aliases
- create immutable revisions
- attach source evidence
- approve or reject candidate data
- merge duplicates while preserving references
- deprecate obsolete records
- inspect usage and downstream impact
- export versioned registry snapshots

All administrative mutations require audit records.

## Import and export

Registry snapshots must support deterministic JSON export with:

- registry_schema_version
- registry_snapshot_id
- source hashes
- generated_at
- record counts
- canonical content hash

Future ModularGrid, CSV, or external registry imports must normalize through the same contracts.

## Testing

Required coverage:

- stable IDs
- alias resolution
- duplicate detection
- revision immutability
- candidate ranking
- unknown preservation
- merge and tombstone behavior
- deterministic snapshot export
- capability graph construction
- migration compatibility

## Release gates

The registry is production-ready only when:

- authoritative sources are retained
- referenced revisions are immutable
- aliases are provenance-bound
- candidate scoring is versioned
- missing data stays explicit
- administrative changes are audited
- deterministic snapshots can be reproduced
- patch generation rejects unresolved required capabilities
