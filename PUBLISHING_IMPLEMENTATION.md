# PatchHive Publishing Layer (Canon v1.7)

## Overview
The publishing layer adds read-only artifact pages for exports, owner publishing controls, public gallery discovery, and moderation workflows with audit logging. Publications are immutable records (status transitions only) and never expose private identifiers.

## Data Model
### `exports`
- `id` (pk)
- `owner_user_id` (fk users)
- `patch_id` (fk patches, nullable)
- `rack_id` (fk racks, nullable)
- `export_type` (`patch` | `rack`)
- `license` (default `CC BY-NC 4.0`)
- `run_id`
- `generated_at`
- `patch_count`
- `manifest_hash`
- `artifact_urls` (json: `pdf`, `svg`, `zip`, optional `waveform_svg`)
- `created_at`, `updated_at`

### `publications`
- `id` (pk)
- `export_id` (fk exports, unique)
- `publisher_user_id` (fk users)
- `slug` (unique)
- `visibility` (`unlisted` | `public`)
- `status` (`draft` | `published` | `hidden` | `removed`)
- `allow_download` (bool)
- `allow_remix` (bool)
- `title`, `description`, `cover_image_url`
- `published_at`, `updated_at`
- `removed_reason`
- `moderation_audit_id` (fk admin_audit_log)

### `publication_reports`
- `id` (pk)
- `publication_id` (fk publications)
- `reporter_user_id` (fk users, nullable)
- `reason`, `details`
- `created_at`

### `admin_audit_log`
- `id` (pk)
- `actor_user_id` (fk users, nullable)
- `action_type`
- `target_type`, `target_id`
- `delta_json` (before/after)
- `reason`
- `created_at`

## API Summary
See [docs/PUBLISHING_API.md](docs/PUBLISHING_API.md) for full routes and schemas.

## Frontend Surfaces
- `/account` → Publishing section with controls for visibility, downloads, title/description edits, hide/unhide.
- `/publish` → Export generation and publication creation flow.
- `/p/{slug}` → Read-only publication page with provenance, license badge, downloads, and report form.
- `/gallery` → Public recency-sorted gallery with export type filter.

## Tests Added
- Export ownership enforcement
- Gallery excludes unlisted
- Removed publication not accessible
- Public payload excludes email/internal IDs
- Download gating
- Moderation audit log

## Git Diff Summary
- Added publishing/admin models, routes, schemas, and auth helpers.
- Added publishing UI pages and API client/types.
- Added publishing documentation.
- Added backend tests for publishing constraints.

## Commit Plan
1. Backend data model + publishing routes + auth helpers
2. Frontend publishing pages and API bindings
3. Documentation + tests
