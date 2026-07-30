# PDB Coverage & Snapshot Metrics — 2026-07-23
**SHA**: 34dd7a228828c96e60da595bce8815e68093589d (main)  
**Source**: Live DB after PR #137 merge + snapshots in data/registry_snapshots/

## Current Metrics (from DB)
- Manufacturers: 705
- Device Models: 376
- (Link rate on catalog side previously ~100% in branch runs)

## Snapshot Assets
- `data/registry_snapshots/registry_latest.json`
- Coverage files generated during ingestion

## Next
- Enhance seeder to emit structured coverage JSON with HP completeness, format distribution, linked %.
- Surface in /api/registry/coverage and explorer.

This advances the "completeness metrics" that were missing in the original PARTIAL device_registry assessment.
