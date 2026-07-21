import { useMemo, useState } from 'react';

type EvidenceState = 'idle' | 'ready' | 'review' | 'confirmed';
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

const DEMO_CANDIDATES: ReviewCandidate[] = [
  {
    id: 'cand-mod-a',
    label: 'Oscillator A',
    manufacturer: 'MockAudio',
    confidence: 0.81,
    alternatives: ['cand-mod-a-alt'],
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

export default function RackBuilderPage() {
  const [evidenceState, setEvidenceState] = useState<EvidenceState>('idle');
  const [fileName, setFileName] = useState('');
  const [error, setError] = useState('');
  const [candidates, setCandidates] = useState<ReviewCandidate[]>(DEMO_CANDIDATES);
  const [inventoryRevisionId, setInventoryRevisionId] = useState<string | null>(null);

  const ranked = useMemo(
    () => [...candidates].sort((a, b) => b.confidence - a.confidence),
    [candidates],
  );

  const allResolved = ranked.every((c) => c.status !== 'inferred');
  const confirmedCount = ranked.filter((c) => c.status === 'confirmed').length;

  const selectPhoto = (file?: File) => {
    setError('');
    setInventoryRevisionId(null);
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 12 * 1024 * 1024) {
      setError('Choose a JPEG, PNG, or WebP image no larger than 12 MB.');
      setEvidenceState('idle');
      return;
    }
    setFileName(file.name);
    setCandidates(DEMO_CANDIDATES.map((c) => ({ ...c, status: 'inferred' as const })));
    setEvidenceState('ready');
  };

  const setStatus = (id: string, status: CandidateStatus) => {
    setCandidates((prev) => prev.map((c) => (c.id === id ? { ...c, status } : c)));
  };

  const createInventoryRevision = () => {
    if (!allResolved || confirmedCount < 1) {
      setError('Confirm at least one module and resolve every candidate before creating a revision.');
      return;
    }
    // Client-side demonstration of immutable revision identity.
    // Server path: POST /api/racks/{id}/evidence/confirmations with module_revision_id per confirm.
    const material = ranked
      .filter((c) => c.status === 'confirmed')
      .map((c) => `${c.id}:${c.moduleRevisionId}`)
      .join('|');
    const syntheticId = `inv-rev-local-${Math.abs(
      Array.from(material).reduce((acc, ch) => (acc * 31 + ch.charCodeAt(0)) | 0, 7),
    ).toString(16)}`;
    setInventoryRevisionId(syntheticId);
    setEvidenceState('confirmed');
    setError('');
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

      <div className="builder-grid">
        <article className="panel">
          <p className="eyebrow">Method 01</p>
          <h2>Manual selection</h2>
          <p className="muted">Search the confirmed module gallery and place exact revisions in your rig.</p>
          <button className="button button-primary" type="button">
            Browse module gallery
          </button>
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
              JPEG, PNG, or WebP · 12 MB maximum. Files are re-encoded and metadata is removed. Multi-image
              API: POST /api/racks/&#123;id&#125;/evidence/images
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
              <button className="button button-secondary" type="button" onClick={() => setEvidenceState('review')}>
                Detect modules
              </button>
            </div>
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
                    Confidence {(candidate.confidence * 100).toFixed(0)}% · method mock_hash_rank
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
                          : candidate.status === 'deferred'
                            ? 'warning'
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
            onClick={createInventoryRevision}
          >
            Create immutable inventory revision
          </button>

          {inventoryRevisionId ? (
            <p className="status status-success" role="status">
              Inventory revision ready: {inventoryRevisionId}. Generation will fail closed without confirmed
              modules (server: inventory_gate NOT_COMPUTABLE).
            </p>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}
