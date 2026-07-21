/**
 * Cases catalog — list with loading / empty / error parity.
 */
import { useEffect, useState } from 'react';
import { caseApi } from '@/lib/api';
import type { Case } from '@/types/api';

type LoadState = 'loading' | 'ready' | 'empty' | 'error';

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [total, setTotal] = useState(0);
  const [state, setState] = useState<LoadState>('loading');
  const [error, setError] = useState('');

  const load = async () => {
    setState('loading');
    setError('');
    try {
      const response = await caseApi.list({ limit: 100 });
      const rows = response.data.cases ?? [];
      setCases(rows);
      setTotal(response.data.total ?? rows.length);
      setState(rows.length === 0 ? 'empty' : 'ready');
    } catch {
      setCases([]);
      setTotal(0);
      setError('Unable to load cases. Check that the API is reachable and try again.');
      setState('error');
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <section aria-labelledby="cases-title">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Catalog</p>
          <h1 id="cases-title">Cases</h1>
          <p className="muted">Browse Eurorack cases used as rack containers for confirmed inventories.</p>
        </div>
        <button className="button button-secondary" type="button" onClick={() => void load()}>
          Refresh
        </button>
      </header>

      {state === 'loading' ? (
        <p className="status" role="status">
          Loading cases…
        </p>
      ) : null}

      {state === 'error' ? (
        <div className="panel" role="alert">
          <p className="status status-danger">{error}</p>
          <button className="button button-primary" type="button" onClick={() => void load()}>
            Retry
          </button>
        </div>
      ) : null}

      {state === 'empty' ? (
        <div className="panel">
          <p className="status status-warning">No cases in the catalog yet.</p>
          <p className="muted">Seed data or admin import will populate this list.</p>
        </div>
      ) : null}

      {state === 'ready' ? (
        <>
          <p className="muted" role="status">
            Showing {cases.length} of {total} cases
          </p>
          <div className="builder-grid" style={{ display: 'grid', gap: '1rem' }}>
            {cases.map((item) => (
              <article key={item.id} className="panel">
                <h2 style={{ color: 'var(--accent, #00ff88)', fontSize: '1.1rem' }}>
                  {item.brand} — {item.name}
                </h2>
                <p className="muted">
                  {item.total_hp} HP · {item.rows} row{item.rows === 1 ? '' : 's'}
                  {item.hp_per_row?.length
                    ? ` · per row: ${item.hp_per_row.join(', ')}`
                    : ''}
                </p>
                {item.description ? <p>{item.description}</p> : null}
                <p className="muted" style={{ fontSize: '0.8rem' }}>
                  Source: {item.source}
                  {item.source_reference ? ` · ${item.source_reference}` : ''}
                </p>
              </article>
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}
