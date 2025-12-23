import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { runApi, monetizationApi, exportApi } from '@/lib/api';
import type { Run } from '@/types/api';

const TOOLTIP_COPY = [
  'This category reflects the structural role of the patch: voice, modulation, rhythm, utility, or experimental.',
  'Difficulty is calculated from modulation depth, routing density, and feedback presence.',
  'This label appears when the patch structure shows unusual complexity or self-interaction.',
  'Each run is a preserved generation. Re-running never overwrites previous results.',
  'This name was generated automatically from the patch structure. You can rename it.',
  'Exports turn patches into printable artifacts. Viewing diagrams is always free.',
  'Credits are only used when exporting. Failed exports do not consume credits.',
  'Functions describe how a jack behaves. Unknown or proprietary functions are flagged for review.',
];

export default function RigDetailPage() {
  const { rigId } = useParams();
  const [runs, setRuns] = useState<Run[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'patches' | 'exports'>('overview');
  const [credits, setCredits] = useState<number>(0);
  const [exportStatus, setExportStatus] = useState<string>('');

  const rigIdNum = Number(rigId);
  const hasRuns = runs.length > 0;

  useEffect(() => {
    if (!rigIdNum) return;
    runApi
      .list(rigIdNum)
      .then((res) => setRuns(res.data.runs))
      .catch(() => setRuns([]));
  }, [rigIdNum]);

  const refreshCredits = () => {
    monetizationApi
      .balance()
      .then((res) => setCredits(res.data.balance))
      .catch(() => setCredits(0));
  };

  useEffect(() => {
    refreshCredits();
  }, []);

  const handleExport = async () => {
    if (!hasRuns) return;
    setExportStatus('');
    try {
      const runId = runs[0].id;
      await exportApi.patchbookExport(runId);
      setExportStatus('Export queued');
      refreshCredits();
    } catch (err: any) {
      setExportStatus(err.response?.data?.detail || 'Export failed');
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Rig {rigId}</h1>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <button
          type="button"
          onClick={() => setActiveTab('overview')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            border: activeTab === 'overview' ? '2px solid #00ff88' : '1px solid #333',
            background: '#111',
            color: '#fff',
          }}
        >
          Overview
        </button>
        {hasRuns && (
          <button
            type="button"
            onClick={() => setActiveTab('patches')}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              border: activeTab === 'patches' ? '2px solid #00ff88' : '1px solid #333',
              background: '#111',
              color: '#fff',
            }}
          >
            Patches
          </button>
        )}
        {hasRuns && (
          <button
            type="button"
            onClick={() => setActiveTab('exports')}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              border: activeTab === 'exports' ? '2px solid #00ff88' : '1px solid #333',
              background: '#111',
              color: '#fff',
            }}
          >
            Exports
          </button>
        )}
      </div>

      {!hasRuns && (
        <p style={{ color: '#888' }}>
          No runs yet. Generate a run to unlock patches and exports.
        </p>
      )}

      {activeTab === 'overview' && (
        <div>
          <p style={{ color: '#ccc' }}>Overview of this rig and its patch runs.</p>
          <p style={{ color: '#888' }}>Runs available: {runs.length}</p>
        </div>
      )}

      {activeTab === 'patches' && hasRuns && (
        <div>
          <h2>Patches</h2>
          <p style={{ color: '#ccc' }}>Generated patches are ready for review.</p>
        </div>
      )}

      {activeTab === 'exports' && hasRuns && (
        <div>
          <h2>Exports</h2>
          <p style={{ color: '#ccc' }}>Credits balance: {credits}</p>
          <button
            type="button"
            onClick={handleExport}
            disabled={credits <= 0}
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '4px',
              border: 'none',
              background: credits > 0 ? '#00ff88' : '#333',
              color: '#000',
              cursor: credits > 0 ? 'pointer' : 'not-allowed',
              fontWeight: 'bold',
            }}
          >
            Export Patch Book
          </button>
          {credits <= 0 && (
            <p style={{ color: '#ff6666', marginTop: '0.5rem' }}>Insufficient credits</p>
          )}
          {exportStatus && <p style={{ color: '#ccc' }}>{exportStatus}</p>}
        </div>
      )}

      <section style={{ marginTop: '2rem' }}>
        <h3>Patch Guidance</h3>
        <ul style={{ color: '#bbb' }}>
          {TOOLTIP_COPY.map((copy) => (
            <li key={copy} style={{ marginBottom: '0.5rem' }}>
              {copy}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
