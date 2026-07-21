import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { evidenceApi, rackApi, type EvidenceCandidate } from '@/lib/api';
import type { Rack } from '@/types/api';

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

export default function RackBuilderPage() {
  const { id: routeId } = useParams<{ id: string }>();
  const rackId = routeId && /^\d+$/.test(routeId) ? Number(routeId) : null;
  const liveMode = rackId != null;

  const [racks, setRacks] = useState<Rack[]>([]);
  const [selectedRackId, setSelectedRackId] = useState<number | null>(rackId);
  const [evidenceState, setEvidenceState] = useState<EvidenceState>('idle');
  const [fileName, setFileName] = useState('');
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [error, setError] = useState('');
  const [candidates, setCandidates] = useState<ReviewCandidate[]>(DEMO_CANDIDATES);
  const [inventoryRevisionId, setInventoryRevisionId] = useState<string | null>(null);
  const [readyForGeneration, setReadyForGeneration] = useState(false);
  const [fromLiveApi, setFromLiveApi] = useState(false);

  const activeRackId = selectedRackId ?? rackId;

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

  const ranked = useMemo(
    () => [...candidates].sort((a, b) => b.confidence - a.confidence),
    [candidates],
  );

  const allResolved = ranked.every((c) => c.status !== 'inferred');
  const confirmedCount = ranked.filter((c) => c.status === 'confirmed').length;

  const selectPhoto = (file?: File) => {
    setError('');
    setInventoryRevisionId(null);
    setReadyForGeneration(false);
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 12 * 1024 * 1024) {
      setError('Choose a JPEG, PNG, or WebP image no larger than 12 MB.');
      setEvidenceState('idle');
      setPendingFile(null);
      return;
    }
    setFileName(file.name);
    setPendingFile(file);
    setFromLiveApi(false);
    setCandidates(DEMO_CANDIDATES.map((c) => ({ ...c, status: 'inferred' as const })));
    setEvidenceState('ready');
  };

  const setStatus = (id: string, status: CandidateStatus) => {
    setCandidates((prev) => prev.map((c) => (c.id === id ? { ...c, status } : c)));
  };

  const detectModules = async () => {
    setError('');
    if (!pendingFile) {
      setError('Choose a rig photo first.');
      return;
    }
    // Live path: upload to evidence API then list ranked candidates.
    if (activeRackId != null) {
      setEvidenceState('uploading');
      try {
        const upload = await evidenceApi.uploadImages(activeRackId, [pendingFile], {
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
        setEvidenceState('review');
      } catch {
        setError('Evidence upload or detection failed. Falling back to local demo candidates.');
        setCandidates(DEMO_CANDIDATES.map((c) => ({ ...c, status: 'inferred' })));
        setFromLiveApi(false);
        setEvidenceState('review');
      }
      return;
    }
    // Create flow without rack: local demo only.
    setFromLiveApi(false);
    setCandidates(DEMO_CANDIDATES.map((c) => ({ ...c, status: 'inferred' })));
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

    // Demo / offline synthetic revision id
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
            Choose modules manually or use a photo as reviewable evidence. Detection is never treated as
            truth.
          </p>
        </div>
      </header>

      {!liveMode ? (
        <div className="panel" style={{ marginBottom: '1rem' }}>
          <p className="muted">
            Photo evidence binds to an existing rig. Select a rig for live upload, or continue with local
            demo detection on this page.
          </p>
          {racks.length > 0 ? (
            <label htmlFor="evidence-rack">
              Target rig for evidence
              <select
                id="evidence-rack"
                value={selectedRackId ?? ''}
                onChange={(event) =>
                  setSelectedRackId(event.target.value ? Number(event.target.value) : null)
                }
                style={{ marginLeft: '0.5rem' }}
              >
                <option value="">Demo only (no API)</option>
                {racks.map((rack) => (
                  <option key={rack.id} value={rack.id}>
                    #{rack.id} · {rack.name}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <p className="muted">
              No rigs loaded. <Link to="/racks">Create a rig</Link> first for live evidence APIs.
            </p>
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
          <p className="eyebrow">Method 02 · evidence acquisition</p>
          <h2 id="photo-title">Review a rig photo</h2>
          <div className="field">
            <label htmlFor="rig-photo">Rig photo</label>
            <input
              id="rig-photo"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              aria-describedby="photo-help photo-error"
              onChange={(event) => selectPhoto(event.target.files?.[0])}
            />
            <span id="photo-help" className="muted">
              JPEG, PNG, or WebP · 12 MB maximum. Files are re-encoded and metadata is removed.
              {activeRackId != null
                ? ` Live API: POST /api/racks/${activeRackId}/evidence/images`
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
              <p className="status status-success">Ready to scan: {fileName}</p>
              <button className="button button-secondary" type="button" onClick={() => void detectModules()}>
                Detect modules
              </button>
            </div>
          ) : null}
          {evidenceState === 'uploading' ? (
            <p className="status" role="status">
              Uploading and detecting…
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
              Confidence is not color-only — status text is always shown.
            </p>
          </div>

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
