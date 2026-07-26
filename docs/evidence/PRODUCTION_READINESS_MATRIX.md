# Production readiness matrix (evidence-bound)

```yaml
assessment:
  source_sha: 9114aae08d368058b2bbe9cfde5c0e6e8e790f60  # re-pin after ops/beta-staging PR merges
  branch: main
  environment: local developer host + CI + local Docker staging (named host NOT_PERFORMED)
  date: "2026-07-26"
  authority_decision: NOT_GRANTED
  production_deployed: false
  production_payments_enabled: false
  full_narrative: PRODUCTION_READINESS_ASSESSMENT_2026-07-21.md
  delta: PRODUCTION_READINESS_DELTA_2026-07-26.md

areas:
  product_scope: PARTIAL  # canon MVP + Design Engine (flags off); dual-path residual
  architecture: PARTIAL  # modular monolith; dual inventory HTTP
  data_model: PARTIAL  # canon + VSI + design engine + device registry + registry slugs
  visual_ingestion: PARTIAL  # secure prep + mock provider; no live model
  module_classification: PARTIAL  # gallery + mock candidates; never self-confirm
  confirmation_workflow: PARTIAL  # multi-photo fusion UI; user confirm only
  device_registry: PARTIAL  # hierarchy + explorer; completeness metrics incomplete
  patch_compiler: PARTIAL  # deterministic compiler + native bridge IDs
  patch_validation: PASS  # unit coverage for graph + inventory gates
  patch_book_compiler: PARTIAL  # Design Engine on main; publication profile flag off
  design_engine: PARTIAL  # default flags false; staging enablement documented
  exports: PARTIAL  # canon exports + pack download; fulfillment flag gated
  frontend: PARTIAL  # MVP routes + PDB explorer + type-safety #141; full page upgrade #96 open
  accessibility: PARTIAL  # graph pair + preflight; WCAG protocol not fully evidenced
  security: PARTIAL  # CI security workflow; prod-only npm high audit; no prod threat sign-off
  privacy: PARTIAL  # EXIF strip; retention policy incomplete
  testing: PARTIAL  # unit/api/CI/e2e; acceptance on Postgres in CI
  migrations: PASS  # single head through 20260726_module_registry_slugs; deploy uses alembic
  deployment: NOT_COMPUTABLE  # no production access; entrypoint fixed for staging path
  backup_and_restore: NOT_COMPUTABLE
  observability: FAIL  # no production SLOs/dashboards evidenced; /health/ready only
  billing: PARTIAL  # test-mode only; live activation forbidden
  support: FAIL  # no support channel evidence
  release_governance: PARTIAL  # VERSIONING + alpha tag; no RC freeze

known_exclusions:
  - audio_processing
  - hardware_control
  - live_stripe
  - community_social_default_on

summary:
  pass:
    - migrations_chain_discipline
    - patch_validation_unit_gates
    - payment_fail_closed_defaults
    - alembic_deploy_entrypoint
  partial:
    - product_scope
    - design_engine
    - visual_ingestion
    - confirmation
    - exports
    - frontend
    - security_privacy
    - device_registry
  fail:
    - observability
    - support
  not_computable:
    - deployment_named_host
    - backup_restore
    - vision_accuracy_metrics
    - multi_tenant_load
  out_of_scope:
    - audio_dsp
    - midi_cv_activation
```

**Do not treat any percentage estimate as readiness.** This matrix supersedes informal readiness percentages in historical notes.

**After merging ops/beta-staging or any release candidate:** update `source_sha`, re-run gates, and append a dated row or new assessment file under `docs/evidence/`.
