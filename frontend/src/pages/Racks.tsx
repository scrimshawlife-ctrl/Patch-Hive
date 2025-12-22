import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { exportApi, patchApi, rackApi, runApi } from '@/lib/api';
import type { Patch, Rack, Run } from '@/types/api';

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
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    category: 'All',
    difficulty: 'All',
    weirdness: 'Any',
  });

  const selectedRack = useMemo(
    () => racks.find((rack) => rack.id === selectedRackId) || null,
    [racks, selectedRackId],
  );

  const hasRuns = runs.length > 0;

  const loadRacks = async () => {
    setError(null);
    try {
      const response = await rackApi.list({ limit: 50 });
      setRacks(response.data.racks);
      if (response.data.racks.length && selectedRackId === null) {
        setSelectedRackId(response.data.racks[0].id);
      }
    } catch (err) {
      setError('Unable to load rigs. Please try again.');
    }
  };

  const loadRuns = async (rackId: number) => {
    try {
      const response = await runApi.list({ rack_id: rackId, limit: 50 });
      setRuns(response.data.runs);
      if (response.data.runs.length) {
        setSelectedRunId(response.data.runs[0].id);
      } else {
        setSelectedRunId(null);
      }
      return response.data.runs;
    } catch (err) {
      setRuns([]);
      setSelectedRunId(null);
      return [];
    }
  };

  const loadPatches = async (runId: number) => {
    try {
      const response = await patchApi.list({ run_id: runId, limit: 100 });
      setPatches(response.data.patches);
    } catch (err) {
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
    } catch (err) {
      setError('Patch generation failed. Please retry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRacks();
  }, []);

  useEffect(() => {
    if (selectedRackId !== null) {
      loadRuns(selectedRackId);
    }
  }, [selectedRackId]);

  useEffect(() => {
    if (selectedRunId !== null) {
      loadPatches(selectedRunId);
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
    <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '2rem' }}>
      <aside style={{ borderRight: '1px solid #222', paddingRight: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0 }}>Rigs</h2>
          <Link to="/racks/new" style={{ color: '#00ff88', textDecoration: 'none' }}>
            New Rig
          </Link>
        </div>
        <p style={{ color: '#777', marginTop: '0.5rem' }}>
          Rig-centric workspace. Each rig carries multiple runs and patch libraries.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {racks.map((rack) => (
            <button
              key={rack.id}
              type="button"
              onClick={() => setSelectedRackId(rack.id)}
              style={{
                textAlign: 'left',
                background: rack.id === selectedRackId ? '#1f1f1f' : '#111',
                border: '1px solid #333',
                padding: '0.75rem',
                borderRadius: '8px',
                color: '#fff',
                cursor: 'pointer',
              }}
            >
              <div style={{ fontWeight: 600 }}>{rack.name}</div>
              <div style={{ fontSize: '0.75rem', color: '#777' }}>
                Suggested: {rack.name_suggested || '—'}
              </div>
            </button>
          ))}
          {racks.length === 0 ? (
            <div style={{ color: '#666', fontSize: '0.9rem' }}>No rigs yet.</div>
          ) : null}
        </div>
      </aside>

      <section>
        {selectedRack ? (
          <>
            <header style={{ marginBottom: '1.5rem' }}>
              <h1 style={{ marginBottom: '0.25rem' }}>{selectedRack.name}</h1>
              <div style={{ color: '#777' }}>{selectedRack.description || 'No rig notes yet.'}</div>
            </header>

            <nav style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
              {tabs.map((tab) => {
                const disabled = (tab.key === 'patches' || tab.key === 'exports') && !hasRuns;
                return (
                  <button
                    key={tab.key}
                    type="button"
                    disabled={disabled}
                    onClick={() => setActiveTab(tab.key)}
                    style={{
                      padding: '0.5rem 0.9rem',
                      borderRadius: '6px',
                      border: '1px solid #333',
                      background: activeTab === tab.key ? '#222' : '#111',
                      color: disabled ? '#444' : '#fff',
                      cursor: disabled ? 'not-allowed' : 'pointer',
                    }}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </nav>

            {error ? (
              <div style={{ background: '#2b0d0d', color: '#ffb3b3', padding: '0.75rem' }}>
                {error}
              </div>
            ) : null}

            {activeTab === 'overview' ? (
              <div style={{ display: 'grid', gap: '1.5rem' }}>
                <div style={{ background: '#111', padding: '1.5rem', borderRadius: '12px' }}>
                  <h3 style={{ marginTop: 0 }}>Rig Summary</h3>
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0, color: '#ccc' }}>
                    <li>Modules: {selectedRack.modules.length}</li>
                    <li>Runs: {runs.length}</li>
                    <li>Latest run: {runs[0]?.created_at || 'None yet'}</li>
                  </ul>
                </div>

                <div style={{ display: 'grid', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    <button
                      type="button"
                      onClick={handleGenerate}
                      disabled={loading}
                      style={{
                        padding: '0.75rem 1.2rem',
                        borderRadius: '8px',
                        border: 'none',
                        background: '#00ff88',
                        color: '#000',
                        fontWeight: 700,
                        cursor: 'pointer',
                      }}
                    >
                      {loading ? 'Generating…' : 'Generate Patch Library'}
                    </button>
                    <Link
                      to="/racks/new"
                      style={{
                        padding: '0.75rem 1.2rem',
                        borderRadius: '8px',
                        border: '1px solid #333',
                        color: '#fff',
                        textDecoration: 'none',
                      }}
                    >
                      Create Rig
                    </Link>
                    <button
                      type="button"
                      style={{
                        padding: '0.75rem 1.2rem',
                        borderRadius: '8px',
                        border: '1px solid #333',
                        background: '#111',
                        color: '#777',
                        cursor: 'not-allowed',
                      }}
                    >
                      Upload Rig (soon)
                    </button>
                  </div>
                  <div style={{ color: '#666' }}>
                    Generate once. Everything else opens as contextual tabs after the rig exists.
                  </div>
                </div>
              </div>
            ) : null}

            {activeTab === 'patches' ? (
              <div style={{ display: 'grid', gap: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  <select
                    value={filters.category}
                    onChange={(event) =>
                      setFilters((prev) => ({ ...prev, category: event.target.value }))
                    }
                    style={{ background: '#111', color: '#fff', padding: '0.4rem' }}
                  >
                    <option>All</option>
                    {[...new Set(patches.map((patch) => patch.category))].map((category) => (
                      <option key={category}>{category}</option>
                    ))}
                  </select>
                  <select
                    value={filters.difficulty}
                    onChange={(event) =>
                      setFilters((prev) => ({ ...prev, difficulty: event.target.value }))
                    }
                    style={{ background: '#111', color: '#fff', padding: '0.4rem' }}
                  >
                    <option>All</option>
                    <option>Beginner</option>
                    <option>Intermediate</option>
                    <option>Advanced</option>
                  </select>
                  <select
                    value={filters.weirdness}
                    onChange={(event) =>
                      setFilters((prev) => ({ ...prev, weirdness: event.target.value }))
                    }
                    style={{ background: '#111', color: '#fff', padding: '0.4rem' }}
                  >
                    <option>Any</option>
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                  </select>
                  <select
                    value={selectedRunId ?? ''}
                    onChange={(event) => setSelectedRunId(Number(event.target.value))}
                    disabled={!hasRuns}
                    style={{ background: '#111', color: '#fff', padding: '0.4rem' }}
                  >
                    {runs.map((run) => (
                      <option key={run.id} value={run.id}>
                        Run #{run.id} • {run.created_at}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ display: 'grid', gap: '0.75rem' }}>
                  {filteredPatches.map((patch) => (
                    <div
                      key={patch.id}
                      style={{ padding: '1rem', border: '1px solid #222', borderRadius: '10px' }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ fontWeight: 600 }}>{patch.name}</div>
                          <div style={{ fontSize: '0.8rem', color: '#777' }}>
                            {patch.suggested_name || 'Suggested name missing'}
                          </div>
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#777' }}>
                          {patch.category} • {difficultyFromConnections(patch)} • Weirdness{' '}
                          {weirdnessFromConnections(patch)}
                        </div>
                      </div>
                      <div style={{ marginTop: '0.75rem', color: '#999', fontSize: '0.9rem' }}>
                        {patch.description || 'No description yet.'}
                      </div>
                    </div>
                  ))}
                  {filteredPatches.length === 0 ? (
                    <div style={{ color: '#666' }}>No patches yet. Generate a run.</div>
                  ) : null}
                </div>
              </div>
            ) : null}

            {activeTab === 'exports' ? (
              <div style={{ display: 'grid', gap: '1rem' }}>
                <div style={{ background: '#111', padding: '1rem', borderRadius: '10px' }}>
                  <h3 style={{ marginTop: 0 }}>Patch Book Exports</h3>
                  <p style={{ color: '#777' }}>
                    Export actions trigger credit checks at download time.
                  </p>
                  <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    <a
                      href={exportApi.rackPdf(selectedRack.id)}
                      style={{ color: '#00ff88', textDecoration: 'none' }}
                    >
                      Export Patch Book PDF
                    </a>
                    <button
                      type="button"
                      style={{
                        border: '1px solid #333',
                        background: '#111',
                        color: '#777',
                        padding: '0.4rem 0.8rem',
                        borderRadius: '6px',
                      }}
                    >
                      Export Selected Patches
                    </button>
                    <button
                      type="button"
                      style={{
                        border: '1px solid #333',
                        background: '#111',
                        color: '#777',
                        padding: '0.4rem 0.8rem',
                        borderRadius: '6px',
                      }}
                    >
                      Export SVG Zip
                    </button>
                  </div>
                </div>
              </div>
            ) : null}

            {activeTab === 'modules' ? (
              <div style={{ display: 'grid', gap: '0.75rem' }}>
                {selectedRack.modules.map((module) => (
                  <div
                    key={module.id}
                    style={{ padding: '0.75rem', border: '1px solid #222', borderRadius: '10px' }}
                  >
                    <div style={{ fontWeight: 600 }}>{module.module?.name || 'Unknown module'}</div>
                    <div style={{ color: '#777', fontSize: '0.85rem' }}>
                      {module.module?.brand || 'Unknown brand'} • {module.module?.module_type || '—'}
                    </div>
                  </div>
                ))}
                {selectedRack.modules.length === 0 ? (
                  <div style={{ color: '#666' }}>No modules loaded for this rig.</div>
                ) : null}
              </div>
            ) : null}
          </>
        ) : (
          <div style={{ color: '#666' }}>Select a rig to begin.</div>
        )}
      </section>
    </div>
  );
}
