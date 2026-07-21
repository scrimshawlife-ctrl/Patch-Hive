import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { caseApi, evidenceApi, rackApi, type EvidenceCandidate } from '@/lib/api';
import type { Case, Rack } from '@/types/api';

type EvidenceState = 'idle' | 'ready' | 'uploading' | 'review' | 'confirmed' | 'error';
type CandidateStatus = 'inferred' | 'confirmed' | 'rejected' | 'deferred';

interface ReviewCandidate {
  id: string;
  label: string;
  manufacturer: string;
  confidence: number;
  alternatives: string[];
  status: CandidateStatus;
  moduleRevisionId: string;
}

interface FusedEntityView {
  fuse_id: string;
  manufacturer?: string | null;
  model?: string | null;
  observation_count: number;
  supporting_image_ids: string[];
  mean_confidence: number;
  conflict: boolean;
  conflict_notes: string[];
  classification_status: string;
  representative_candidate_id?: string | null;
}

/** Demo ranked set when no rack id is available (create flow). */
const DEMO_CANDIDATES: ReviewCandidate[] = [
  {
    id: 'cand-mod-a',
    label: 'Oscillator A',
    manufacturer: 'MockAudio',
    confidence: 0.81,
    alternatives: ['cand-mod-a-alt · higher-gain rev'],
    status: 'inferred',
    moduleRevisionId: 'catalog-module-osc-a',
  },
  {
    id: 'cand-mod-b',
    label: 'VCA B',
    manufacturer: 'MockAudio',
    confidence: 0.64,
    alternatives: [],
    status: 'inferred',
    moduleRevisionId: 'catalog-module-vca-b',
  },
];

function mapApiCandidates(rows: EvidenceCandidate[]): ReviewCandidate[] {
  return rows.map((row) => ({
    id: row.candidate_id,
    label: row.model || row.entity_type || row.candidate_id,
    manufacturer: row.manufacturer || 'Unknown',
    confidence: row.confidence,
    alternatives: row.alternative_candidates ?? [],
    status: 'inferred',
    moduleRevisionId:
      row.gallery_revision_id ||
      (row.gallery_module_id ? `gallery-${row.gallery_module_id}` : `catalog-${row.candidate_id}`),
  }));
}

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_BYTES = 12 * 1024 * 1024;

function casePowerSummary(c: Case): string {
  const parts: string[] = [];
  if (c.power_12v_ma != null) parts.push(`+12 ${c.power_12v_ma}mA`);
  if (c.power_neg12v_ma != null) parts.push(`−12 ${c.power_neg12v_ma}mA`);
  if (c.power_5v_ma != null) parts.push(`+5 ${c.power_5v_ma}mA`);
  if (parts.length) return parts.join(' · ');
  if (c.meta?.powered === false) return 'Unpowered';
  return 'Power unspecified (placement will not enforce rails)';
}

function formatValidationError(err: unknown): string {
  const apiError = err as {
    response?: { data?: { detail?: string | { message?: string; errors?: { field?: string; message?: string }[] } } };
  };
  const detail = apiError.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (detail && typeof detail === 'object') {
    const errs = detail.errors;
    if (Array.isArray(errs) && errs.length) {
      return errs.map((e) => e.message || e.field || 'Validation error').join(' · ');
    }
    if (detail.message) return detail.message;
  }
  return 'Could not create rig. Check case selection and try again.';
}

export default function RackBuilderPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { id: routeId } = useParams<{ id: string }>();
  const rackId = routeId && /^\d+$/.test(routeId) ? Number(routeId) : null;
  const liveMode = rackId != null;
  const preselectedCaseId = Number(searchParams.get('case_id') || '') || null;

  const [racks, setRacks] = useState<Rack[]>([]);
  const [selectedRackId, setSelectedRackId] = useState<number | null>(rackId);
  const [evidenceState, setEvidenceState] = useState<EvidenceState>('idle');
  const [fileLabel, setFileLabel] = useState('');
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [error, setError] = useState('');
  const [candidates, setCandidates] = useState<ReviewCandidate[]>(DEMO_CANDIDATES);
  const [inventoryRevisionId, setInventoryRevisionId] = useState<string | null>(null);
  const [readyForGeneration, setReadyForGeneration] = useState(false);
  const [fromLiveApi, setFromLiveApi] = useState(false);
  const [fused, setFused] = useState<FusedEntityView[]>([]);
  /** User-applied fusion decisions keyed by fuse_id (still maps to candidate rows). */
  const [fusedApplied, setFusedApplied] = useState<Record<string, CandidateStatus>>({});
  const [fusionFeedback, setFusionFeedback] = useState<string | null>(null);
  const [reconcileStatus, setReconcileStatus] = useState<string | null>(null);
  const [reconcileNote, setReconcileNote] = useState<string | null>(null);
  const [imageCount, setImageCount] = useState(0);

  /** C0: case-bound create on /racks/new */
  const [cases, setCases] = useState<Case[]>([]);
  const [casesLoading, setCasesLoading] = useState(false);
  const [selectedCaseId, setSelectedCaseId] = useState<number | null>(preselectedCaseId);
  const [rigName, setRigName] = useState('');
  const [creating, setCreating] = useState(false);
  const [caseQuery, setCaseQuery] = useState('');

  const activeRackId = selectedRackId ?? rackId;
  const selectedCase = useMemo(
    () => cases.find((c) => c.id === selectedCaseId) ?? null,
    [cases, selectedCaseId],
  );

  useEffect(() => {
    if (rackId != null) {
      setSelectedRackId(rackId);
      return;
    }
    rackApi
      .list({ limit: 50 })
      .then((res) => {
        setRacks(res.data.racks ?? []);
        if (res.data.racks?.length && selectedRackId == null) {
          setSelectedRackId(res.data.racks[0].id);
        }
      })
      .catch(() => {
        setRacks([]);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- initial rack list only
  }, [rackId]);

  useEffect(() => {
    if (liveMode) return;
    setCasesLoading(true);
    caseApi
      .list({ limit: 200, format_family: 'Eurorack', q: caseQuery.trim() || undefined })
      .then((res) => {
        const rows = res.data.cases ?? [];
        setCases(rows);
        if (selectedCaseId == null && preselectedCaseId != null) {
          setSelectedCaseId(preselectedCaseId);
        } else if (selectedCaseId == null && rows.length === 1) {
          setSelectedCaseId(rows[0].id);
        }
      })
      .catch(() => setCases([]))
      .finally(() => setCasesLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps -- case catalog load
  }, [liveMode, caseQuery]);

  const createRigFromCase = async () => {
    if (selectedCaseId == null) {
      setError('Select a Eurorack case before creating a rig.');
      return;
    }
    setCreating(true);
    setError('');
    try {
      const res = await rackApi.create({
        case_id: selectedCaseId,
        name: rigName.trim() || undefined,
        modules: [],
      });
      const id = res.data.id;
      navigate(`/racks/${id}/edit`);
    } catch (err) {
      setError(formatValidationError(err));
    } finally {
      setCreating(false);
    }
  };

  const ranked = useMemo(
    () => [...candidates].sort((a, b) => b.confidence - a.confidence),
    [candidates],
  );

  const allResolved = ranked.every((c) => c.status !== 'inferred');
  const confirmedCount = ranked.filter((c) => c.status === 'confirmed').length;

  const selectPhotos = (list?: FileList | null) => {
    setError('');
    setInventoryRevisionId(null);
    setReadyForGeneration(false);
    setFused([]);
    setFusedApplied({});
    setFusionFeedback(null);
    setReconcileStatus(null);
    setReconcileNote(null);
    setImageCount(0);
    if (!list || list.length === 0) return;

    const accepted: File[] = [];
    const reasons: string[] = [];
    Array.from(list).forEach((file) => {
      if (!ALLOWED_TYPES.includes(file.type) || file.size > MAX_BYTES) {
        reasons.push(`${file.name}: type/size rejected`);
        return;
      }
      accepted.push(file);
    });
    if (!accepted.length) {
      setError(reasons.join('; ') || 'Choose JPEG, PNG, or WebP images ≤ 12 MB.');
      setEvidenceState('idle');
      setPendingFiles([]);
      return;
    }
    if (reasons.length) {
      setError(`Some files skipped: ${reasons.join('; ')}`);
    }
    setPendingFiles(accepted);
    setFileLabel(
      accepted.length === 1
        ? accepted[0].name
        : `${accepted.length} photos (${accepted.map((f) => f.name).join(', ')})`,
    );
    setFromLiveApi(false);
    setCandidates(DEMO_CANDIDATES.map((c) => ({ ...c, status: 'inferred' as const })));
    setEvidenceState('ready');
  };

  const setStatus = (id: string, status: CandidateStatus) => {
    setCandidates((prev) => prev.map((c) => (c.id === id ? { ...c, status } : c)));
  };

  /** Apply a fusion-panel decision onto the matching candidate row (still user-initiated). */
  const applyFusedDecision = (entity: FusedEntityView, status: CandidateStatus) => {
    const targetId = entity.representative_candidate_id;
    if (!targetId) {
      setError('Fused entity has no representative candidate id to resolve.');
      setFusionFeedback(null);
      return;
    }
    if (entity.conflict && status === 'confirmed') {
      setError(
        'Cannot confirm a conflicted fusion from the panel — resolve the underlying candidates individually.',
      );
      setFusionFeedback(null);
      return;
    }
    setError('');
    setStatus(targetId, status);
    setFusedApplied((prev) => ({ ...prev, [entity.fuse_id]: status }));
    const label = entity.model || entity.fuse_id;
    setFusionFeedback(`Applied ${status} to fused “${label}” (candidate ${targetId}).`);
  };

  const confirmAllNonConflictFused = () => {
    setError('');
    const eligible = fused.filter((e) => !e.conflict && e.representative_candidate_id);
    const confirmIds = new Set(eligible.map((e) => e.representative_candidate_id as string));
    const blocked = fused.length - confirmIds.size;
    if (!confirmIds.size) {
      setError(
        blocked
          ? 'No non-conflict fused entities to confirm. Resolve conflicts in the candidate list.'
          : 'No fused entities available.',
      );
      setFusionFeedback(null);
      return;
    }
    setCandidates((prev) =>
      prev.map((c) => (confirmIds.has(c.id) ? { ...c, status: 'confirmed' as const } : c)),
    );
    setFusedApplied((prev) => {
      const next = { ...prev };
      eligible.forEach((e) => {
        next[e.fuse_id] = 'confirmed';
      });
      return next;
    });
    setFusionFeedback(
      `Confirmed ${eligible.length} non-conflict fusion${eligible.length === 1 ? '' : 's'}` +
        (blocked ? ` · ${blocked} blocked (conflict or missing rep)` : ''),
    );
  };

  const detectModules = async () => {
    setError('');
    if (!pendingFiles.length) {
      setError('Choose at least one rig photo first.');
      return;
    }
    // Live path: multi-image upload → candidates → multi-photo reconcile
    if (activeRackId != null) {
      setEvidenceState('uploading');
      try {
        const upload = await evidenceApi.uploadImages(activeRackId, pendingFiles, {
          run_vision_mock: true,
          consent_provider_processing: false,
        });
        if (upload.data.rejected?.length && !upload.data.uploaded?.length) {
          setError(upload.data.rejected.map((r) => `${r.filename}: ${r.reason}`).join('; '));
          setEvidenceState('error');
          return;
        }
        const listed = await evidenceApi.listCandidates(activeRackId);
        const mapped = mapApiCandidates(listed.data.candidates ?? []);
        if (mapped.length) {
          setCandidates(mapped);
          setFromLiveApi(true);
        } else {
          setCandidates(DEMO_CANDIDATES.map((c) => ({ ...c, status: 'inferred' })));
          setFromLiveApi(false);
        }
        try {
          const recon = await evidenceApi.reconcile(activeRackId);
          setFused(recon.data.fused_entities ?? []);
          setFusedApplied({});
          setFusionFeedback(null);
          setReconcileStatus(recon.data.status);
          setReconcileNote(recon.data.note);
          setImageCount(recon.data.image_count);
        } catch {
          setFused([]);
          setFusedApplied({});
          setReconcileStatus(null);
          setReconcileNote('Reconciliation API unavailable; showing per-image candidates only.');
        }
        setEvidenceState('review');
      } catch {
        setError('Evidence upload or detection failed. Falling back to local demo candidates.');
        setCandidates(DEMO_CANDIDATES.map((c) => ({ ...c, status: 'inferred' })));
        setFromLiveApi(false);
        setFused([]);
        setEvidenceState('review');
      }
      return;
    }
    // Create flow without rack: local demo only.
    setFromLiveApi(false);
    setCandidates(DEMO_CANDIDATES.map((c) => ({ ...c, status: 'inferred' })));
    setFused([]);
    setReconcileStatus(pendingFiles.length >= 2 ? 'DEMO_MULTI' : 'DEMO_SINGLE');
    setReconcileNote(
      pendingFiles.length >= 2
        ? 'Demo mode: multi-photo fusion requires a live rig target.'
        : 'Demo mode: select a rig for live multi-photo reconciliation.',
    );
    setEvidenceState('review');
  };

  const createInventoryRevision = async () => {
    if (!allResolved || confirmedCount < 1) {
      setError('Confirm at least one module and resolve every candidate before creating a revision.');
      return;
    }
    setError('');

    if (activeRackId != null && fromLiveApi) {
      try {
        const decisions = ranked.map((c) => {
          if (c.status === 'confirmed') {
            return {
              candidate_id: c.id,
              status: 'confirm',
              module_revision_id: c.moduleRevisionId,
            };
          }
          if (c.status === 'rejected') {
            return { candidate_id: c.id, status: 'reject' };
          }
          return { candidate_id: c.id, status: 'defer' };
        });
        const result = await evidenceApi.confirm(activeRackId, {
          confirmed_by: 'workspace-user',
          decisions,
        });
        setInventoryRevisionId(result.data.inventory_revision_id);
        setReadyForGeneration(result.data.ready_for_generation);
        setEvidenceState('confirmed');
        return;
      } catch {
        setError('Confirmation API failed. Inventory was not persisted.');
        return;
      }
    }

    const material = ranked
      .filter((c) => c.status === 'confirmed')
      .map((c) => `${c.id}:${c.moduleRevisionId}`)
      .join('|');
    const syntheticId = `inv-rev-local-${Math.abs(
      Array.from(material).reduce((acc, ch) => (acc * 31 + ch.charCodeAt(0)) | 0, 7),
    ).toString(16)}`;
    setInventoryRevisionId(syntheticId);
    setReadyForGeneration(true);
    setEvidenceState('confirmed');
  };

  return (
    <section aria-labelledby="builder-title">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Create rig</p>
          <h1 id="builder-title">Establish your module inventory</h1>
          <p className="muted">
            Bind a Eurorack case, then place modules manually or review photo evidence. Multi-photo
            fusion never auto-confirms inventory. Missing case power stays unchecked.
          </p>
        </div>
      </header>

      {!liveMode ? (
        <div className="panel" style={{ marginBottom: 'var(--space-4)' }} aria-labelledby="case-step-title">
          <p className="eyebrow">Step 0 · required</p>
          <h2 id="case-step-title" style={{ marginTop: 0 }}>
            Choose a case envelope
          </h2>
          <p className="muted">
            Only Eurorack cases are selectable for placement. Other formats remain catalog-only on{' '}
            <Link to="/cases">Cases</Link>.
          </p>
          <div className="toolbar" style={{ marginTop: 'var(--space-3)' }}>
            <label className="field" style={{ flex: '1 1 12rem' }}>
              Search cases
              <input
                type="search"
                value={caseQuery}
                placeholder="Brand or model…"
                onChange={(e) => setCaseQuery(e.target.value)}
              />
            </label>
            <label className="field" style={{ flex: '1 1 14rem' }}>
              Case
              <select
                value={selectedCaseId ?? ''}
                onChange={(e) =>
                  setSelectedCaseId(e.target.value ? Number(e.target.value) : null)
                }
                disabled={casesLoading}
                aria-required
              >
                <option value="">{casesLoading ? 'Loading…' : 'Select Eurorack case…'}</option>
                {cases.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.brand} — {c.name} ({c.total_hp}HP · {c.rows} row
                    {c.rows === 1 ? '' : 's'})
                  </option>
                ))}
              </select>
            </label>
            <label className="field" style={{ flex: '1 1 10rem' }}>
              Rig name (optional)
              <input
                type="text"
                value={rigName}
                onChange={(e) => setRigName(e.target.value)}
                placeholder="Auto-named if empty"
              />
            </label>
            <button
              type="button"
              className="button button-primary"
              onClick={() => void createRigFromCase()}
              disabled={creating || selectedCaseId == null}
            >
              {creating ? 'Creating…' : 'Create empty rig'}
            </button>
          </div>
          {selectedCase ? (
            <div className="stat-row" style={{ marginTop: 'var(--space-4)' }}>
              <div className="stat-block">
                <p className="muted" style={{ margin: 0 }}>
                  Layout
                </p>
                <h3 style={{ fontSize: '1rem' }}>
                  {selectedCase.hp_per_row?.join(' + ') || selectedCase.total_hp} HP
                </h3>
              </div>
              <div className="stat-block">
                <p className="muted" style={{ margin: 0 }}>
                  Power
                </p>
                <h3 style={{ fontSize: '1rem' }}>{casePowerSummary(selectedCase)}</h3>
              </div>
            </div>
          ) : null}
          {error && !liveMode ? (
            <p className="status status-danger" role="alert" style={{ marginTop: 'var(--space-3)' }}>
              {error}
            </p>
          ) : null}
          {!casesLoading && cases.length === 0 ? (
            <p className="status status-warning" style={{ marginTop: 'var(--space-3)' }}>
              No Eurorack cases in catalog. Import with <code>just cases-import</code> or open{' '}
              <Link to="/cases">Cases</Link>.
            </p>
          ) : null}

          <hr style={{ border: 0, borderTop: '1px solid var(--border)', margin: 'var(--space-5) 0' }} />

          <p className="muted">
            Photo evidence binds to an existing rig. Select a rig for live multi-photo upload, or continue
            with local demo detection after create.
          </p>
          {racks.length > 0 ? (
            <label className="field" htmlFor="evidence-rack" style={{ maxWidth: '24rem' }}>
              Target rig for evidence
              <select
                id="evidence-rack"
                value={selectedRackId ?? ''}
                onChange={(event) =>
                  setSelectedRackId(event.target.value ? Number(event.target.value) : null)
                }
              >
                <option value="">Demo only (no API)</option>
                {racks.map((rack) => (
                  <option key={rack.id} value={rack.id}>
                    #{rack.id} · {rack.name}
                    {rack.case_id != null ? ` · case #${rack.case_id}` : ''}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <p className="muted">Create a case-bound rig above to enable live evidence APIs.</p>
          )}
        </div>
      ) : (
        <p className="muted">
          Live evidence mode for rig #{rackId}.{' '}
          <Link to={`/rigs/${rackId}`}>Open rig detail</Link>
        </p>
      )}

      <div className="builder-grid">
        <article className="panel">
          <p className="eyebrow">Method 01</p>
          <h2>Manual selection</h2>
          <p className="muted">Search the confirmed module gallery and place exact revisions in your rig.</p>
          <Link className="button button-primary" to="/modules">
            Browse module gallery
          </Link>
        </article>

        <article className="panel" aria-labelledby="photo-title">
          <p className="eyebrow">Method 02 · multi-photo evidence</p>
          <h2 id="photo-title">Review rig photo(s)</h2>
          <div className="field">
            <label htmlFor="rig-photo">Rig photo</label>
            <input
              id="rig-photo"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              multiple
              aria-describedby="photo-help photo-error"
              onChange={(event) => selectPhotos(event.target.files)}
            />
            <span id="photo-help" className="muted">
              JPEG, PNG, or WebP · 12 MB each · multiple angles supported.
              {activeRackId != null
                ? ` Live: upload + GET /api/racks/${activeRackId}/evidence/reconcile`
                : ' Demo mode until a target rig is selected.'}
            </span>
            {error ? (
              <span id="photo-error" role="alert" className="status status-danger">
                {error}
              </span>
            ) : null}
          </div>
          {evidenceState === 'ready' ? (
            <div className="evidence-ready">
              <p className="status status-success">Ready to scan: {fileLabel}</p>
              <button className="button button-secondary" type="button" onClick={() => void detectModules()}>
                Detect modules
              </button>
            </div>
          ) : null}
          {evidenceState === 'uploading' ? (
            <p className="status" role="status">
              Uploading {pendingFiles.length} image(s) and reconciling…
            </p>
          ) : null}
        </article>
      </div>

      {evidenceState === 'review' || evidenceState === 'confirmed' ? (
        <section className="panel evidence-review" aria-labelledby="review-title">
          <div>
            <p className="eyebrow">Human confirmation required</p>
            <h2 id="review-title">Review ranked detection candidates</h2>
            <p className="muted">
              Provider suggestions remain inferred until you confirm an authoritative gallery match.
              Multi-photo fusion is advisory only.
            </p>
          </div>

          {(fused.length > 0 || reconcileStatus) && (
            <div className="panel" aria-label="Multi-photo reconciliation" style={{ marginBottom: '1rem' }}>
              <h3>Multi-photo reconciliation</h3>
              <p className="muted" role="status">
                Status: {reconcileStatus ?? '—'}
                {imageCount ? ` · ${imageCount} image(s)` : ''}
                {reconcileNote ? ` · ${reconcileNote}` : ''}
              </p>
              {fused.length === 0 ? (
                <p className="muted">No fused entities yet.</p>
              ) : (
                <>
                  <div style={{ marginBottom: '0.75rem' }}>
                    <button
                      className="button button-secondary"
                      type="button"
                      onClick={confirmAllNonConflictFused}
                      disabled={evidenceState === 'confirmed'}
                    >
                      Confirm all non-conflict fused
                    </button>
                    <p className="muted" style={{ marginTop: '0.5rem' }}>
                      Applies confirm only to non-conflict fusions via their representative candidate.
                      Conflicts must be resolved in the candidate list below.
                    </p>
                    {fusionFeedback ? (
                      <p className="status status-success" role="status" style={{ marginTop: '0.5rem' }}>
                        {fusionFeedback}
                      </p>
                    ) : null}
                  </div>
                  <ul style={{ listStyle: 'none', padding: 0 }} aria-label="Fused module entities">
                    {fused.map((entity) => {
                      const applied = fusedApplied[entity.fuse_id];
                      const statusClass = entity.conflict
                        ? 'danger'
                        : applied === 'confirmed'
                          ? 'success'
                          : applied === 'rejected'
                            ? 'danger'
                            : 'warning';
                      const statusText = entity.conflict
                        ? `Conflict: ${entity.conflict_notes.join('; ') || 'disagreement'}`
                        : applied
                          ? `Applied: ${applied}`
                          : `Status: ${entity.classification_status} (not confirmed)`;
                      return (
                        <li
                          key={entity.fuse_id}
                          className="detection-row"
                          style={{ marginBottom: '0.75rem' }}
                        >
                          <div>
                            <strong>
                              {entity.manufacturer || 'Unknown'} · {entity.model || entity.fuse_id}
                            </strong>
                            <p className="muted">
                              Support: {entity.observation_count} observation(s) across{' '}
                              {entity.supporting_image_ids.length} image(s) · mean confidence{' '}
                              {(entity.mean_confidence * 100).toFixed(0)}%
                              {entity.representative_candidate_id
                                ? ' · linked to ranked candidate'
                                : ' · no representative candidate'}
                            </p>
                            <p className={`status status-${statusClass}`}>{statusText}</p>
                          </div>
                          <div
                            className="detection-actions"
                            aria-label={`Resolve fused ${entity.model || entity.fuse_id}`}
                          >
                            <button
                              className="button button-secondary"
                              type="button"
                              disabled={
                                entity.conflict ||
                                !entity.representative_candidate_id ||
                                evidenceState === 'confirmed'
                              }
                              onClick={() => applyFusedDecision(entity, 'confirmed')}
                            >
                              Confirm fused match
                            </button>
                            <button
                              className="button button-quiet"
                              type="button"
                              disabled={
                                !entity.representative_candidate_id || evidenceState === 'confirmed'
                              }
                              onClick={() => applyFusedDecision(entity, 'rejected')}
                            >
                              Reject fused
                            </button>
                            <button
                              className="button button-quiet"
                              type="button"
                              disabled={
                                !entity.representative_candidate_id || evidenceState === 'confirmed'
                              }
                              onClick={() => applyFusedDecision(entity, 'deferred')}
                            >
                              Defer fused
                            </button>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </>
              )}
            </div>
          )}

          <ul className="candidate-list" aria-label="Ranked module candidates">
            {ranked.map((candidate) => (
              <li key={candidate.id} className="detection-row">
                <div>
                  <strong>
                    {candidate.manufacturer} · {candidate.label}
                  </strong>
                  <p className="muted">
                    Confidence {(candidate.confidence * 100).toFixed(0)}%
                    {candidate.alternatives.length
                      ? ` · alternatives: ${candidate.alternatives.join(', ')}`
                      : ''}
                  </p>
                  <p
                    className={`status status-${
                      candidate.status === 'confirmed'
                        ? 'success'
                        : candidate.status === 'rejected'
                          ? 'danger'
                          : 'warning'
                    }`}
                  >
                    Status: {candidate.status}
                  </p>
                </div>
                <div className="detection-actions" aria-label={`Resolve ${candidate.label}`}>
                  <button
                    className="button button-secondary"
                    type="button"
                    onClick={() => setStatus(candidate.id, 'confirmed')}
                  >
                    Confirm match
                  </button>
                  <button
                    className="button button-quiet"
                    type="button"
                    onClick={() => setStatus(candidate.id, 'rejected')}
                  >
                    Reject
                  </button>
                  <button
                    className="button button-quiet"
                    type="button"
                    onClick={() => setStatus(candidate.id, 'deferred')}
                  >
                    Defer
                  </button>
                </div>
              </li>
            ))}
          </ul>

          <p className="muted" role="status">
            {confirmedCount} confirmed · {ranked.length - confirmedCount} not confirmed · all resolved:{' '}
            {allResolved ? 'yes' : 'no'}
          </p>

          <button
            className="button button-primary"
            type="button"
            disabled={!allResolved || confirmedCount < 1 || evidenceState === 'confirmed'}
            onClick={() => void createInventoryRevision()}
          >
            Create immutable rig revision
          </button>

          {inventoryRevisionId ? (
            <p className="status status-success" role="status">
              Inventory revision ready: {inventoryRevisionId}
              {readyForGeneration ? ' · ready for generation' : ' · not ready for generation'}.
              {activeRackId != null ? (
                <>
                  {' '}
                  <Link to={`/rigs/${activeRackId}`}>Generate patches on this rig</Link>
                </>
              ) : null}
            </p>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}
