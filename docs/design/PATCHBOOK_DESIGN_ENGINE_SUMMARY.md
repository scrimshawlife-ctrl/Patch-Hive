# Summary: PatchHive PatchBook Design Engine

**Date:** 2026-07-20  
**Revision:** r3 (content load path + multi-patch + resolve-before-debit)  
**Status:** **Approved** — design-doc review consensus; **MVP implementation in progress** (contracts, resolver, content spine Path B, fulfillment, branding, flags)  
**Doc:** `grok-design-doc-4f16883c.md`

## What was designed

A **PatchBook Export Design Engine** for PatchHive (Zero State product): deterministic publishing + **canon export fulfillment**, with a concrete **Layer A load path** that matches today’s product generate → bridge → debit flow.

## Content spine (r3 — critical)

| Path | When | Source |
|------|------|--------|
| **B (MVP default)** | No `GeneratedPatchRecord` rows | `seal_orm_patch_to_compilation` from run-bound ORM `Patch.connections` + sealed `RigRevisionRecord` — **not** live rack re-query, **not** `builder.py` |
| **A (steady state)** | Dual-write at generate | Load `GeneratedPatchRecord` by library `position` |
| Bridge `artifact_manifest_hash` | Always | **Binding key only** (KD-19); integrity = `library_content_hash` |

Multi-patch: ordered `list[PatchCompilation]`; all-or-nothing fail+refund; pack includes `source/library_index.json`.

## Other r3 decisions

- **Resolve recipe before debit** (and on preview); worker re-validates only (`DESIGN_RECIPE_RESOLVE_DRIFT`); snapshot `resolved_tier`.
- **Dual-run** both adapters from sealed multi-patch fixtures + field parity checklist (not live ORM builder).
- **Worker contract:** max 5 attempts, 15m lease, idempotent succeed, inline = post-commit sync fulfill.

## Four surfaces (unchanged framing)

Canon ledger (debit/queued) · Legacy ReportLab · Canon export_pack JSON · CLI ArtifactStore

## Review status

| Pass | Open → addressed |
|------|------------------|
| r2 | 22 |
| r3 re-review | **6** (0 open) |

## MVP PRs (01–10)

Contracts → flags → resolver → **content load Path B/A** → **fulfillment** → branding → **resolve-before-debit + recipe columns** → engine + dual-run fixtures → preview → Style Studio

## Next implementation step

**PR-04:** `load_patch_compilations` + `seal_orm_patch_to_compilation` (+ generate dual-write), then **PR-05** fulfillment against real RigDetail runs.
