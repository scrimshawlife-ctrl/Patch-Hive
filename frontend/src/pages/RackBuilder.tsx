import { useState } from 'react';

type EvidenceState = 'idle' | 'ready' | 'review';

export default function RackBuilderPage() {
  const [evidenceState, setEvidenceState] = useState<EvidenceState>('idle');
  const [fileName, setFileName] = useState('');
  const [error, setError] = useState('');
  const [resolution, setResolution] = useState<'inferred' | 'confirmed' | 'disputed'>('inferred');

  const selectPhoto = (file?: File) => {
    setError('');
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 12 * 1024 * 1024) {
      setError('Choose a JPEG, PNG, or WebP image no larger than 12 MB.');
      setEvidenceState('idle');
      return;
    }
    setFileName(file.name);
    setEvidenceState('ready');
  };

  return (
    <section aria-labelledby="builder-title">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Create rig</p>
          <h1 id="builder-title">Establish your module inventory</h1>
          <p className="muted">Choose modules manually or use a photo as reviewable evidence. Detection is never treated as truth.</p>
        </div>
      </header>

      <div className="builder-grid">
        <article className="panel">
          <p className="eyebrow">Method 01</p>
          <h2>Manual selection</h2>
          <p className="muted">Search the confirmed module gallery and place exact revisions in your rig.</p>
          <button className="button button-primary" type="button">Browse module gallery</button>
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
            <span id="photo-help" className="muted">JPEG, PNG, or WebP · 12 MB maximum. Files are re-encoded and metadata is removed.</span>
            {error ? <span id="photo-error" role="alert" className="status status-danger">{error}</span> : null}
          </div>
          {evidenceState === 'ready' ? (
            <div className="evidence-ready">
              <p className="status status-success">Ready to scan: {fileName}</p>
              <button className="button button-secondary" type="button" onClick={() => setEvidenceState('review')}>Detect modules</button>
            </div>
          ) : null}
        </article>
      </div>

      {evidenceState === 'review' ? (
        <section className="panel evidence-review" aria-labelledby="review-title">
          <div>
            <p className="eyebrow">Human confirmation required</p>
            <h2 id="review-title">Review detection evidence</h2>
            <p className="muted">Provider suggestions remain inferred until you confirm an authoritative gallery match.</p>
          </div>
          <article className="detection-row">
            <div>
              <strong>Possible oscillator module</strong>
              <p className={`status status-${resolution === 'confirmed' ? 'success' : resolution === 'disputed' ? 'danger' : 'warning'}`}>Status: {resolution}</p>
            </div>
            <div className="detection-actions" aria-label="Resolve possible oscillator module">
              <button className="button button-secondary" type="button" onClick={() => setResolution('confirmed')}>Confirm match</button>
              <button className="button button-quiet" type="button" onClick={() => setResolution('disputed')}>Dispute</button>
            </div>
          </article>
          <button className="button button-primary" type="button" disabled={resolution === 'inferred'}>Create immutable rig revision</button>
        </section>
      ) : null}
    </section>
  );
}
