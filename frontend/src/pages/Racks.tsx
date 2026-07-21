import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { canonApi, exportApi, patchApi, rackApi, runApi } from '@/lib/api';
import type { CompatibilityResponse, Patch, Rack, Run } from '@/types/api';

type TabKey = 'overview' | 'patches' | 'exports' | 'modules';

const tabs: { key: TabKey; label: string }[] = [
  { key: 'overview', label: 'Overview' },
  { key: 'patches', label: 'Patches' },
  { key: 'exports', label: 'Exports' },
  { key: 'modules', label: 'Module Gallery' },
];

const difficultyFromConnections = (patch: Patch) => {
  const count = patch.connections?.length || 0;
  if (count <= 4) return 'Beginner';
  if (count <= 8) return 'Intermediate';
  return 'Advanced';
};

const weirdnessFromConnections = (patch: Patch) => {
  const modulationEdges = patch.connections.filter((c) =>
    ['cv', 'gate', 'clock'].includes(c.cable_type),
  ).length;
  return Math.min(100, modulationEdges * 8);
};

export default function RacksPage() {
  const [racks, setRacks] = useState<Rack[]>([]);
  const [selectedRackId, setSelectedRackId] = useState<number | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [patches, setPatches] = useState<Patch[]>([]);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    category: 'All',
    difficulty: 'All',
    weirdness: 'Any',
  });
  const [compat, setCompat] = useState<{
    bridge_status: string;
    message: string;
    catalog_slug?: string | null;
    compatibility?: CompatibilityResponse | null;
  } | null>(null);
  const [compatLoading, setCompatLoading] = useState(false);

  const selectedRack = useMemo(
    () => racks.find((rack) => rack.id === selectedRackId) || null,
    [racks, selectedRackId],
  );

  const hasRuns = runs.length > 0;

  const loadRacks = async () => {
    setError(null);
    setListLoading(true);
    try {
      const response = await rackApi.list({ limit: 50 });
      setRacks(response.data.racks);
      if (response.data.racks.length && selectedRackId === null) {
        setSelectedRackId(response.data.racks[0].id);
      }
    } catch {
      setRacks([]);
      setError('Unable to load rigs. Please try again.');
    } finally {
      setListLoading(false);
    }
  };

  const loadRuns = async (rackId: number) => {
    try {
      const response = await canonApi.listRuns(rackId);
      setRuns(response.data.runs);
      if (response.data.runs.length) {
        setSelectedRunId(response.data.runs[0].id);
      } else {
        setSelectedRunId(null);
      }
      return response.data.runs;
    } catch {
      setRuns([]);
      setSelectedRunId(null);
      return [];
    }
  };

  const loadCompat = async (rackId: number) => {
    setCompatLoading(true);
    try {
      const res = await rackApi.compatibility(rackId);
      setCompat(res.data);
    } catch {
      setCompat(null);
    } finally {
      setCompatLoading(false);
    }
  };

  const loadPatches = async (runId: number) => {
    try {
      const response = await runApi.patches(runId);
      setPatches(response.data.patches);
    } catch {
      setPatches([]);
    }
  };

  const handleGenerate = async () => {
    if (!selectedRack) return;
    setLoading(true);
    setError(null);
    try {
      await patchApi.generate(selectedRack.id, {});
      const latestRuns = await loadRuns(selectedRack.id);
      if (latestRuns[0]?.id) {
        await loadPatches(latestRuns[0].id);
      }
      setActiveTab('patches');
    } catch {
      setError('Patch generation failed. Please retry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadRacks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedRackId !== null) {
      void loadRuns(selectedRackId);
      void loadCompat(selectedRackId);
    } else {
      setCompat(null);
    }
  }, [selectedRackId]);

  useEffect(() => {
    if (selectedRunId !== null) {
      void loadPatches(selectedRunId);
    } else {
      setPatches([]);
    }
  }, [selectedRunId]);

  const filteredPatches = patches.filter((patch) => {
    if (filters.category !== 'All' && patch.category !== filters.category) return false;
    const difficulty = difficultyFromConnections(patch);
    if (filters.difficulty !== 'All' && difficulty !== filters.difficulty) return false;
    const weirdness = weirdnessFromConnections(patch);
    if (filters.weirdness === 'Low' && weirdness > 25) return false;
    if (filters.weirdness === 'Medium' && (weirdness < 25 || weirdness > 60)) return false;
    if (filters.weirdness === 'High' && weirdness < 60) return false;
    return true;
  });

  return (
    <div className="split-workspace">
      <aside className="split-aside" aria-label="Rig list">
        <div className="split-aside-head">
          <h2>Rigs</h2>
          <Link className="button button-primary" to="/racks/new">
            New
          </Link>
        </div>
        <p className="muted" style={{ margin: 0, fontSize: '0.9rem' }}>
          Rig-centric workspace. Each rig carries runs and patch libraries.
        </p>
        <div className="side-list">
          {listLoading ? (
            <p className="status" role="status">
              Loading rigs…
            </p>
          ) : null}
          {!listLoading && error && racks.length === 0 ? (
            <div className="panel" role="alert">
              <p className="status status-danger">{error}</p>
              <button className="button button-secondary" type="button" onClick={() => void loadRacks()}>
                Retry
              </button>
            </div>
          ) : null}
          {!listLoading
            ? racks.map((rack) => (
                <button
                  key={rack.id}
                  type="button"
                  className={`side-item${rack.id === selectedRackId ? ' is-selected' : ''}`}
                  aria-current={rack.id === selectedRackId ? 'true' : undefined}
                  onClick={() => setSelectedRackId(rack.id)}
                >
                  <span className="side-item-title">{rack.name}</span>
                  <span className="side-item-meta">
                    Suggested: {rack.name_suggested || '—'}
                  </span>
                </button>
              ))
            : null}
          {!listLoading && racks.length === 0 && !error ? (
            <div className="panel">
              <p className="status status-warning">No rigs yet.</p>
              <Link className="button button-primary" to="/racks/new">
                Create your first rig
              </Link>
            </div>
          ) : null}
        </div>
      </aside>

      <section aria-label="Selected rig workspace">
        {selectedRack ? (
          <>
            <header className="workspace-header">
              <div>
                <p className="eyebrow">Rig workspace</p>
                <h1>{selectedRack.name}</h1>
                <p className="muted">{selectedRack.description || 'No rig notes yet.'}</p>
              </div>
            </header>

            <nav className="tab-list" role="tablist" aria-label="Rig sections">
              {tabs.map((tab) => {
                const disabled = (tab.key === 'patches' || tab.key === 'exports') && !hasRuns;
                return (
                  <button
                    key={tab.key}
                    type="button"
                    role="tab"
                    className="tab"
                    aria-selected={activeTab === tab.key}
                    disabled={disabled}
                    onClick={() => setActiveTab(tab.key)}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </nav>

            {error ? (
              <div className="panel" role="alert" style={{ marginBottom: 'var(--space-4)' }}>
                <p className="status status-danger">{error}</p>
              </div>
            ) : null}

            {activeTab === 'overview' ? (
              <div style={{ display: 'grid', gap: 'var(--space-5)' }}>
                <div className="panel">
                  <p className="eyebrow">Summary</p>
                  <h2 style={{ marginTop: 0 }}>Rig inventory</h2>
                  <div className="stat-row" style={{ marginTop: 'var(--space-4)' }}>
                    <div className="stat-block">
                      <p className="muted" style={{ margin: 0 }}>
                        Modules
                      </p>
                      <h3>{selectedRack.modules.length}</h3>
                    </div>
                    <div className="stat-block">
                      <p className="muted" style={{ margin: 0 }}>
                        Runs
                      </p>
                      <h3>{runs.length}</h3>
                    </div>
                    <div className="stat-block">
                      <p className="muted" style={{ margin: 0 }}>
                        Latest run
                      </p>
                      <h3 style={{ fontSize: '1rem' }}>{runs[0]?.created_at || 'None yet'}</h3>
                    </div>
                  </div>
                  {selectedRack.case ? (
                    <p className="muted" style={{ marginBottom: 0, marginTop: 'var(--space-3)' }}>
                      Case: {selectedRack.case.brand} — {selectedRack.case.name}
                      {selectedRack.case.catalog_slug
                        ? ` · catalog ${selectedRack.case.catalog_slug}`
                        : ' · not linked to normalized catalog'}
                    </p>
                  ) : null}
                </div>

                <div className="panel" aria-live="polite">
                  <p className="eyebrow">Catalog compatibility</p>
                  <h2 style={{ marginTop: 0 }}>Case fit report</h2>
                  {compatLoading ? (
                    <p className="muted">Loading compatibility…</p>
                  ) : compat ? (
                    <>
                      <p>
                        Bridge: <strong>{compat.bridge_status}</strong>
                        {compat.catalog_slug ? ` · ${compat.catalog_slug}` : ''}
                      </p>
                      <p className="muted">{compat.message}</p>
                      {compat.compatibility ? (
                        <>
                          <p>
                            Overall:{' '}
                            <strong>{compat.compatibility.overall_status}</strong>
                          </p>
                          <ul>
                            <li>
                              Format: {compat.compatibility.format_check.status}
                            </li>
                            <li>
                              Physical fit: {compat.compatibility.physical_fit.status}
                            </li>
                            <li>
                              Connectors: {compat.compatibility.connector_availability.status}
                            </li>
                            <li>+5V: {compat.compatibility.pos5_compatibility.status}</li>
                          </ul>
                          {compat.compatibility.power_headroom?.length ? (
                            <ul>
                              {compat.compatibility.power_headroom.map((r) => (
                                <li key={r.rail}>
                                  {r.rail}: {r.status}
                                  {r.headroom_ma != null ? ` · headroom ${r.headroom_ma}mA` : ''}
                                </li>
                              ))}
                            </ul>
                          ) : null}
                        </>
                      ) : null}
                    </>
                  ) : (
                    <p className="muted">Compatibility unavailable for this rig.</p>
                  )}
                </div>

                <div className="panel">
                  <div className="page-hero-actions">
                    <button
                      type="button"
                      className="button button-primary"
                      onClick={() => void handleGenerate()}
                      disabled={loading}
                    >
                      {loading ? 'Generating…' : 'Generate patch library'}
                    </button>
                    <Link
                      className="button button-secondary"
                      to={`/racks/${selectedRack.id}/edit`}
                    >
                      Place modules
                    </Link>
                    <Link className="button button-secondary" to="/racks/new">
                      Create rig
                    </Link>
                    <button type="button" className="button button-quiet" disabled>
                      Upload rig (soon)
                    </button>
                  </div>
                  <p className="muted" style={{ marginBottom: 0, marginTop: 'var(--space-3)' }}>
                    Generate once. Patches and exports open as tabs after a run exists. Placement
                    uses catalog compatibility when the case is materialized.
                  </p>
                </div>
              </div>
            ) : null}

            {activeTab === 'patches' ? (
              <div style={{ display: 'grid', gap: 'var(--space-4)' }}>
                <div className="panel toolbar" aria-label="Patch filters">
                  <label className="inline-field">
                    Category
                    <select
                      value={filters.category}
                      onChange={(event) =>
                        setFilters((prev) => ({ ...prev, category: event.target.value }))
                      }
                    >
                      <option>All</option>
                      {[...new Set(patches.map((patch) => patch.category))].map((category) => (
                        <option key={category}>{category}</option>
                      ))}
                    </select>
                  </label>
                  <label className="inline-field">
                    Difficulty
                    <select
                      value={filters.difficulty}
                      onChange={(event) =>
                        setFilters((prev) => ({ ...prev, difficulty: event.target.value }))
                      }
                    >
                      <option>All</option>
                      <option>Beginner</option>
                      <option>Intermediate</option>
                      <option>Advanced</option>
                    </select>
                  </label>
                  <label className="inline-field">
                    Weirdness
                    <select
                      value={filters.weirdness}
                      onChange={(event) =>
                        setFilters((prev) => ({ ...prev, weirdness: event.target.value }))
                      }
                    >
                      <option>Any</option>
                      <option>Low</option>
                      <option>Medium</option>
                      <option>High</option>
                    </select>
                  </label>
                  <label className="inline-field">
                    Run
                    <select
                      value={selectedRunId ?? ''}
                      onChange={(event) => setSelectedRunId(Number(event.target.value))}
                      disabled={!hasRuns}
                    >
                      {runs.map((run) => (
                        <option key={run.id} value={run.id}>
                          Run #{run.id} · {run.created_at}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="catalog-grid">
                  {filteredPatches.map((patch) => (
                    <article key={patch.id} className="catalog-card">
                      <h3>{patch.name}</h3>
                      <p className="catalog-card-meta">
                        {patch.suggested_name || 'Suggested name missing'}
                      </p>
                      <p className="muted" style={{ margin: 0, fontSize: '0.85rem' }}>
                        {patch.category} · {difficultyFromConnections(patch)} · weirdness{' '}
                        {weirdnessFromConnections(patch)}
                      </p>
                      <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        {patch.description || 'No description yet.'}
                      </p>
                    </article>
                  ))}
                </div>
                {filteredPatches.length === 0 ? (
                  <div className="panel">
                    <p className="status status-warning">No patches yet. Generate a run.</p>
                  </div>
                ) : null}
              </div>
            ) : null}

            {activeTab === 'exports' ? (
              <div className="panel">
                <p className="eyebrow">PatchBooks</p>
                <h2 style={{ marginTop: 0 }}>Exports</h2>
                <p className="muted">
                  Export actions trigger credit checks at download time. Credits debit only at the
                  canonical boundary.
                </p>
                <div className="page-hero-actions">
                  <a className="button button-primary" href={exportApi.rackPdf(selectedRack.id)}>
                    Export Patch Book PDF
                  </a>
                  <button type="button" className="button button-quiet" disabled>
                    Export selected patches
                  </button>
                  <button type="button" className="button button-quiet" disabled>
                    Export SVG zip
                  </button>
                </div>
              </div>
            ) : null}

            {activeTab === 'modules' ? (
              <div className="catalog-grid">
                {selectedRack.modules.map((module) => (
                  <article key={module.id} className="catalog-card">
                    <h3>{module.module?.name || 'Unknown module'}</h3>
                    <p className="catalog-card-meta">
                      {module.module?.brand || 'Unknown brand'} ·{' '}
                      {module.module?.module_type || '—'} · {module.module?.hp ?? '—'}HP
                      {module.module?.depth_mm != null
                        ? ` · depth ${module.module.depth_mm}mm`
                        : ' · depth unspecified'}
                    </p>
                    <p className="muted" style={{ margin: 0, fontSize: '0.85rem' }}>
                      Row {module.row_index} · start HP {module.start_hp}
                      {module.module?.power_12v_ma != null
                        ? ` · +12 ${module.module.power_12v_ma}mA`
                        : ''}
                    </p>
                  </article>
                ))}
                {selectedRack.modules.length === 0 ? (
                  <div className="panel">
                    <p className="status status-warning">No modules loaded for this rig.</p>
                    <Link
                      className="button button-secondary"
                      to={`/racks/${selectedRack.id}/edit`}
                    >
                      Place modules
                    </Link>
                  </div>
                ) : (
                  <div className="panel">
                    <Link
                      className="button button-secondary"
                      to={`/racks/${selectedRack.id}/edit`}
                    >
                      Edit placements
                    </Link>
                  </div>
                )}
              </div>
            ) : null}
          </>
        ) : (
          <div className="panel">
            <p className="eyebrow">Workspace</p>
            <h2 style={{ marginTop: 0 }}>Select a rig to begin</h2>
            <p className="muted">Choose a rig from the list, or create a new one to confirm inventory.</p>
            <Link className="button button-primary" to="/racks/new">
              New rig
            </Link>
          </div>
        )}
      </section>
    </div>
  );
}
