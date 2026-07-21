import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { canonApi } from '@/lib/api';
import type { Run } from '@/types/api';

type WorkspaceTab = 'overview' | 'patches' | 'exports' | 'gallery';

const tabLabels: Record<WorkspaceTab, string> = {
  overview: 'Overview',
  patches: 'Patches',
  exports: 'Exports',
  gallery: 'Module gallery',
};

export default function RigDetailPage() {
  const { rigId } = useParams();
  const rigIdNum = Number(rigId);
  const [runs, setRuns] = useState<Run[]>([]);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('overview');
  const [activeRunId, setActiveRunId] = useState<number | null>(null);
  const [credits, setCredits] = useState(0);
  const [exportStatus, setExportStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const hasRuns = runs.length > 0;
  const tabs = useMemo<WorkspaceTab[]>(
    () => (hasRuns ? ['overview', 'patches', 'exports', 'gallery'] : ['overview', 'gallery']),
    [hasRuns],
  );
  const activeRun = useMemo(
    () => runs.find((run) => run.id === activeRunId) ?? null,
    [runs, activeRunId],
  );

  useEffect(() => {
    if (!rigIdNum) return;
    setLoading(true);
    canonApi
      .listRuns(rigIdNum)
      .then((response) => {
        const ordered = [...response.data.runs].sort(
          (a, b) => Date.parse(b.created_at) - Date.parse(a.created_at),
        );
        setRuns(ordered);
        setActiveRunId(ordered[0]?.id ?? null);
      })
      .catch(() => setRuns([]))
      .finally(() => setLoading(false));
  }, [rigIdNum]);

  const refreshCredits = () => {
    canonApi
      .getBalance()
      .then((response) => setCredits(response.data.balance))
      .catch(() => setCredits(0));
  };

  useEffect(refreshCredits, []);

  const handleExport = async () => {
    if (!activeRun) return;
    if (!activeRun.export_bridge_ready) {
      setExportStatus('Export bridge not ready for this run; reload the workspace and retry.');
      return;
    }
    setExportStatus('');
    setExporting(true);
    try {
      const idempotency_key = `patchbook-run-${activeRun.id}-${crypto.randomUUID()}`;
      const created = await canonApi.createExport({
        source_run_id: activeRun.source_run_id,
        source_rig_revision_id: activeRun.rig_revision_id,
        artifact_manifest_hash: activeRun.artifact_manifest_hash,
        formats: ['pdf', 'json'],
        license: 'personal',
        idempotency_key,
      });
      setExportStatus(
        `Canonical export ${created.data.export_id} ${created.data.status}. Credits debited on the /api/canon ledger only.`,
      );
      refreshCredits();
    } catch (error: unknown) {
      const apiError = error as { response?: { data?: { detail?: string }; status?: number } };
      const detail = apiError.response?.data?.detail;
      if (apiError.response?.status === 402) {
        setExportStatus('INSUFFICIENT_CREDITS — no debit recorded on the canonical ledger.');
      } else {
        setExportStatus(detail || 'Export failed; no successful canonical debit recorded.');
      }
    } finally {
      setExporting(false);
    }
  };

  return (
    <section aria-labelledby="rig-title">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Canonical rig workspace</p>
          <h1 id="rig-title">Rig {rigId}</h1>
          <p className="muted">Revisions and runs are preserved; personal patch notes remain editable.</p>
        </div>
        {hasRuns ? (
          <div className="field">
            <label htmlFor="run-selector">Source run</label>
            <select
              id="run-selector"
              value={activeRunId ?? ''}
              onChange={(event) => setActiveRunId(Number(event.target.value))}
            >
              {runs.map((run, index) => (
                <option key={run.id} value={run.id}>
                  {index === 0 ? 'Latest · ' : ''}Run {run.id} · {new Date(run.created_at).toLocaleDateString()}
                </option>
              ))}
            </select>
          </div>
        ) : null}
      </header>

      <div className="tab-list" role="tablist" aria-label="Rig workspace">
        {tabs.map((tab) => (
          <button
            className="tab"
            id={`tab-${tab}`}
            key={tab}
            type="button"
            role="tab"
            aria-selected={activeTab === tab}
            aria-controls={`panel-${tab}`}
            onClick={() => setActiveTab(tab)}
          >
            {tabLabels[tab]}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="panel" role="status">
          Loading rig history…
        </div>
      ) : null}

      {!loading && activeTab === 'overview' ? (
        <div className="panel" id="panel-overview" role="tabpanel" aria-labelledby="tab-overview">
          <h2>{hasRuns ? 'Rig ready' : 'Build the source of truth'}</h2>
          <p className="muted">
            {hasRuns
              ? `${runs.length} immutable generation ${runs.length === 1 ? 'run' : 'runs'} available.`
              : 'Add modules manually or review photo evidence before generating.'}
          </p>
          {!hasRuns ? (
            <button className="button button-primary" type="button">
              Generate patch library
            </button>
          ) : null}
        </div>
      ) : null}

      {!loading && activeTab === 'patches' && hasRuns ? (
        <div className="panel" id="panel-patches" role="tabpanel" aria-labelledby="tab-patches">
          <p className="eyebrow">Run {activeRunId}</p>
          <h2>Patch library</h2>
          <p className="muted">Inspect graph, cable table, five-phase plan, validation, and variations.</p>
        </div>
      ) : null}

      {!loading && activeTab === 'exports' && hasRuns ? (
        <div className="panel" id="panel-exports" role="tabpanel" aria-labelledby="tab-exports">
          <p className="eyebrow">Canonical monetization boundary</p>
          <h2>Exports</h2>
          <p>
            Available credits: <strong>{credits}</strong>
          </p>
          <p className="muted">Debits post only via <code>/api/canon/exports</code>.</p>
          <button
            className="button button-primary"
            type="button"
            onClick={handleExport}
            disabled={credits <= 0 || exporting || !activeRunId}
          >
            {exporting ? 'Requesting…' : 'Export PDF patch book'}
          </button>
          {credits <= 0 ? (
            <p className="status status-warning">Credits are required only for exports.</p>
          ) : null}
          {exportStatus ? (
            <p role="status" className="status">
              {exportStatus}
            </p>
          ) : null}
        </div>
      ) : null}

      {!loading && activeTab === 'gallery' ? (
        <div className="panel" id="panel-gallery" role="tabpanel" aria-labelledby="tab-gallery">
          <p className="eyebrow">Evidence and revisions</p>
          <h2>Module gallery</h2>
          <p className="muted">
            Confirmed gallery evidence is separated from inferred, disputed, and missing specifications.
          </p>
        </div>
      ) : null}
    </section>
  );
}
