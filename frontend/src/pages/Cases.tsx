/**
 * Cases catalog — filters, format honesty, link into new rig (C0).
 */
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { caseApi } from '@/lib/api';
import type { Case } from '@/types/api';

type LoadState = 'loading' | 'ready' | 'empty' | 'error';

function formatFamily(item: Case): string {
  const meta = item.meta ?? {};
  const family = typeof meta.format_family === 'string' ? meta.format_family : '';
  return family || 'Eurorack';
}

function capacityLabel(item: Case): string {
  const meta = item.meta ?? {};
  const unit = typeof meta.capacity_unit === 'string' ? meta.capacity_unit : 'hp';
  if (unit === 'hp' || !unit) {
    return `${item.total_hp} HP · ${item.rows} row${item.rows === 1 ? '' : 's'}${
      item.hp_per_row?.length ? ` · ${item.hp_per_row.join(' + ')}` : ''
    }`;
  }
  return `${item.total_hp} ${unit.replace(/_/g, ' ')} · ${item.rows} row${
    item.rows === 1 ? '' : 's'
  }`;
}

function powerLabel(item: Case): string {
  const parts: string[] = [];
  if (item.power_12v_ma != null) parts.push(`+12 ${item.power_12v_ma}mA`);
  if (item.power_neg12v_ma != null) parts.push(`−12 ${item.power_neg12v_ma}mA`);
  if (item.power_5v_ma != null) parts.push(`+5 ${item.power_5v_ma}mA`);
  if (parts.length) return parts.join(' · ');
  const meta = item.meta ?? {};
  if (meta.powered === false) return 'Unpowered (no rails published)';
  return 'Power unspecified (not checked at placement)';
}

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [total, setTotal] = useState(0);
  const [state, setState] = useState<LoadState>('loading');
  const [error, setError] = useState('');
  const [q, setQ] = useState('');
  const [formatFamilyFilter, setFormatFamilyFilter] = useState('Eurorack');
  const [poweredFilter, setPoweredFilter] = useState<'all' | 'yes' | 'no'>('all');
  const [minHp, setMinHp] = useState('');

  const load = async () => {
    setState('loading');
    setError('');
    try {
      const response = await caseApi.list({
        limit: 200,
        q: q.trim() || undefined,
        format_family: formatFamilyFilter || undefined,
        powered:
          poweredFilter === 'all' ? undefined : poweredFilter === 'yes' ? true : false,
        min_hp: minHp ? Number(minHp) : undefined,
      });
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
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reload on filter change
  }, [formatFamilyFilter, poweredFilter]);

  const brands = useMemo(() => {
    const set = new Set(cases.map((c) => c.brand));
    return Array.from(set).sort();
  }, [cases]);

  return (
    <section aria-labelledby="cases-title">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Catalog</p>
          <h1 id="cases-title">Cases</h1>
          <p className="muted">
            Case envelopes for rig placement. Missing power or depth stays missing — never invented.
            Eurorack is the default placement format.
          </p>
        </div>
        <div className="header-actions">
          <Link className="button button-primary" to="/racks/new">
            New rig
          </Link>
          <button className="button button-secondary" type="button" onClick={() => void load()}>
            Refresh
          </button>
        </div>
      </header>

      <div className="panel toolbar" style={{ marginBottom: 'var(--space-4)' }} aria-label="Case filters">
        <label className="field" style={{ flex: '1 1 12rem' }}>
          Search
          <input
            type="search"
            value={q}
            placeholder="Brand or model…"
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') void load();
            }}
          />
        </label>
        <label className="inline-field">
          Format
          <select
            value={formatFamilyFilter}
            onChange={(e) => setFormatFamilyFilter(e.target.value)}
          >
            <option value="">All formats</option>
            <option value="Eurorack">Eurorack</option>
            <option value="Buchla">Buchla</option>
            <option value="5U MU">5U MU</option>
            <option value="Serge 4U">Serge 4U</option>
            <option value="Frac">Frac</option>
          </select>
        </label>
        <label className="inline-field">
          Powered
          <select
            value={poweredFilter}
            onChange={(e) => setPoweredFilter(e.target.value as 'all' | 'yes' | 'no')}
          >
            <option value="all">Any</option>
            <option value="yes">Powered</option>
            <option value="no">Unpowered</option>
          </select>
        </label>
        <label className="inline-field">
          Min HP / capacity
          <input
            type="number"
            min={0}
            value={minHp}
            onChange={(e) => setMinHp(e.target.value)}
            style={{ width: '6rem' }}
          />
        </label>
        <button className="button button-secondary" type="button" onClick={() => void load()}>
          Apply
        </button>
      </div>

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
          <p className="status status-warning">No cases match these filters.</p>
          <p className="muted">
            Import research catalog with <code>just cases-import</code> or clear filters.
          </p>
        </div>
      ) : null}

      {state === 'ready' ? (
        <>
          <p className="muted" role="status" style={{ marginBottom: 'var(--space-4)' }}>
            Showing {cases.length} of {total} cases
            {brands.length ? ` · ${brands.length} brands in view` : ''}
          </p>
          <div className="catalog-grid">
            {cases.map((item) => {
              const family = formatFamily(item);
              const canPlace = family.toLowerCase() === 'eurorack';
              return (
                <article key={item.id} className="catalog-card">
                  <span className="feature-card-icon" aria-hidden="true">
                    {family.slice(0, 2).toUpperCase()}
                  </span>
                  <h2>
                    {item.brand} — {item.name}
                  </h2>
                  <p className="catalog-card-meta">{capacityLabel(item)}</p>
                  <p className="catalog-card-meta">{powerLabel(item)}</p>
                  <p className="muted" style={{ margin: 0, fontSize: '0.85rem' }}>
                    {family}
                    {item.description ? ` · ${item.description}` : ''}
                  </p>
                  <div className="page-hero-actions">
                    {canPlace ? (
                      <Link
                        className="button button-primary"
                        to={`/racks/new?case_id=${item.id}`}
                      >
                        Use on new rig
                      </Link>
                    ) : (
                      <span className="status status-warning">Catalog only (non-Eurorack)</span>
                    )}
                    <Link className="button button-quiet" to="/racks">
                      Open rigs
                    </Link>
                  </div>
                </article>
              );
            })}
          </div>
        </>
      ) : null}
    </section>
  );
}
