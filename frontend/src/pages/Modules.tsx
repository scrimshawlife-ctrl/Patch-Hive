/**
 * Module Library page - Browse and manage modules.
 */
import { useState, useEffect } from 'react';
import { moduleApi } from '@/lib/api';
import type { Module } from '@/types/api';

type LoadState = 'loading' | 'ready' | 'empty' | 'error';

export default function ModulesPage() {
  const [modules, setModules] = useState<Module[]>([]);
  const [state, setState] = useState<LoadState>('loading');
  const [error, setError] = useState('');

  const load = () => {
    setState('loading');
    setError('');
    moduleApi
      .list({ limit: 100 })
      .then((res) => {
        const rows = res.data.modules ?? [];
        setModules(rows);
        setState(rows.length === 0 ? 'empty' : 'ready');
      })
      .catch(() => {
        setModules([]);
        setError('Unable to load modules.');
        setState('error');
      });
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <section aria-labelledby="modules-title">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Catalog</p>
          <h1 id="modules-title">Module gallery</h1>
          <p className="muted">Confirmed module specifications for inventory placement.</p>
        </div>
        <button className="button button-secondary" type="button" onClick={load}>
          Refresh
        </button>
      </header>

      {state === 'loading' ? (
        <p className="status" role="status">
          Loading modules…
        </p>
      ) : null}

      {state === 'error' ? (
        <div className="panel" role="alert">
          <p className="status status-danger">{error}</p>
          <button className="button button-primary" type="button" onClick={load}>
            Retry
          </button>
        </div>
      ) : null}

      {state === 'empty' ? (
        <div className="panel">
          <p className="status status-warning">No modules in the gallery yet.</p>
        </div>
      ) : null}

      {state === 'ready' ? (
        <>
          <p className="muted" role="status">
            Total modules: {modules.length}
          </p>
          <div style={{ display: 'grid', gap: '1rem' }}>
            {modules.map((module) => (
              <article
                key={module.id}
                className="panel"
                style={{
                  padding: '1rem',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <div>
                    <h2 style={{ color: 'var(--accent, #00ff88)', marginBottom: '0.5rem', fontSize: '1.1rem' }}>
                      {module.brand} - {module.name}
                    </h2>
                    <p className="muted" style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                      {module.module_type} | {module.hp}HP
                    </p>
                    {module.description ? (
                      <p style={{ color: '#888', fontSize: '0.875rem' }}>{module.description}</p>
                    ) : null}
                  </div>
                  <div style={{ textAlign: 'right', color: '#666', fontSize: '0.75rem' }}>
                    <div>Power: +12V {module.power_12v_ma}mA</div>
                    {module.power_neg12v_ma ? <div>-12V {module.power_neg12v_ma}mA</div> : null}
                  </div>
                </div>
              </article>
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}
