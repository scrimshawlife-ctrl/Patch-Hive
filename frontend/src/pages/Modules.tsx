/**
 * Module gallery — browse confirmed catalog modules for inventory placement.
 */
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { moduleApi } from '@/lib/api';
import type { Module } from '@/types/api';

type LoadState = 'loading' | 'ready' | 'empty' | 'error';
type SortKey = 'brand' | 'name' | 'hp' | 'type';

export default function ModulesPage() {
  const [modules, setModules] = useState<Module[]>([]);
  const [state, setState] = useState<LoadState>('loading');
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [brandFilter, setBrandFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortKey, setSortKey] = useState<SortKey>('brand');

  const load = () => {
    setState('loading');
    setError('');
    moduleApi
      .list({ limit: 200 })
      .then((res) => {
        const rows = res.data.modules ?? [];
        setModules(rows);
        setState(rows.length === 0 ? 'empty' : 'ready');
      })
      .catch(() => {
        setModules([]);
        setError('Unable to load modules. Check that the API is reachable and try again.');
        setState('error');
      });
  };

  useEffect(() => {
    load();
  }, []);

  const brands = useMemo(() => {
    const set = new Set(modules.map((m) => m.brand).filter(Boolean));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [modules]);

  const types = useMemo(() => {
    const set = new Set(modules.map((m) => m.module_type).filter(Boolean));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [modules]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let rows = modules.filter((m) => {
      if (brandFilter !== 'all' && m.brand !== brandFilter) return false;
      if (typeFilter !== 'all' && m.module_type !== typeFilter) return false;
      if (!q) return true;
      const hay = `${m.brand} ${m.name} ${m.module_type} ${m.description ?? ''}`.toLowerCase();
      return hay.includes(q);
    });
    rows = [...rows].sort((a, b) => {
      if (sortKey === 'hp') return (a.hp ?? 0) - (b.hp ?? 0) || a.name.localeCompare(b.name);
      if (sortKey === 'name') return a.name.localeCompare(b.name);
      if (sortKey === 'type')
        return a.module_type.localeCompare(b.module_type) || a.name.localeCompare(b.name);
      return a.brand.localeCompare(b.brand) || a.name.localeCompare(b.name);
    });
    return rows;
  }, [modules, query, brandFilter, typeFilter, sortKey]);

  const clearFilters = () => {
    setQuery('');
    setBrandFilter('all');
    setTypeFilter('all');
    setSortKey('brand');
  };

  const filtersActive = query.trim() || brandFilter !== 'all' || typeFilter !== 'all';

  return (
    <section aria-labelledby="modules-title">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Catalog</p>
          <h1 id="modules-title">Module gallery</h1>
          <p className="muted">
            Confirmed module specifications for inventory placement. Detection never auto-confirms
            inventory — place modules on a rig or review photo evidence.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Link className="button button-primary" to="/racks/new">
            Place on new rig
          </Link>
          <button className="button button-secondary" type="button" onClick={load}>
            Refresh
          </button>
        </div>
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
          <p className="muted">Seed data or admin import will populate this list.</p>
        </div>
      ) : null}

      {state === 'ready' ? (
        <>
          <div className="panel" aria-label="Module filters" style={{ marginBottom: '1rem' }}>
            <div
              style={{
                display: 'grid',
                gap: '0.75rem',
                gridTemplateColumns: 'repeat(auto-fit, minmax(12rem, 1fr))',
                alignItems: 'end',
              }}
            >
              <label className="field" htmlFor="module-search">
                Search
                <input
                  id="module-search"
                  type="search"
                  value={query}
                  placeholder="Brand, name, type…"
                  onChange={(event) => setQuery(event.target.value)}
                  autoComplete="off"
                />
              </label>
              <label className="field" htmlFor="module-brand">
                Brand
                <select
                  id="module-brand"
                  value={brandFilter}
                  onChange={(event) => setBrandFilter(event.target.value)}
                >
                  <option value="all">All brands</option>
                  {brands.map((brand) => (
                    <option key={brand} value={brand}>
                      {brand}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field" htmlFor="module-type">
                Type
                <select
                  id="module-type"
                  value={typeFilter}
                  onChange={(event) => setTypeFilter(event.target.value)}
                >
                  <option value="all">All types</option>
                  {types.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field" htmlFor="module-sort">
                Sort
                <select
                  id="module-sort"
                  value={sortKey}
                  onChange={(event) => setSortKey(event.target.value as SortKey)}
                >
                  <option value="brand">Brand</option>
                  <option value="name">Name</option>
                  <option value="type">Type</option>
                  <option value="hp">HP (width)</option>
                </select>
              </label>
            </div>
            {filtersActive ? (
              <p style={{ marginTop: '0.75rem', marginBottom: 0 }}>
                <button className="button button-quiet" type="button" onClick={clearFilters}>
                  Clear filters
                </button>
              </p>
            ) : null}
          </div>

          <p className="muted" role="status">
            Showing {filtered.length} of {modules.length} modules
            {filtersActive ? ' (filtered)' : ''}
          </p>

          {filtered.length === 0 ? (
            <div className="panel">
              <p className="status status-warning">No modules match these filters.</p>
              <button className="button button-secondary" type="button" onClick={clearFilters}>
                Clear filters
              </button>
            </div>
          ) : (
            <ul
              aria-label="Module catalog results"
              style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: '1rem' }}
            >
              {filtered.map((module) => (
                <li key={module.id}>
                  <article className="panel" style={{ padding: '1rem' }}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'start',
                        gap: '1rem',
                        flexWrap: 'wrap',
                      }}
                    >
                      <div>
                        <h2
                          style={{
                            color: 'var(--accent, #00ff88)',
                            marginBottom: '0.5rem',
                            fontSize: '1.1rem',
                          }}
                        >
                          {module.brand} — {module.name}
                        </h2>
                        <p className="muted" style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                          {module.module_type} · {module.hp}HP
                        </p>
                        {module.description ? (
                          <p style={{ color: '#888', fontSize: '0.875rem' }}>{module.description}</p>
                        ) : null}
                      </div>
                      <div style={{ textAlign: 'right', color: '#666', fontSize: '0.75rem' }}>
                        <div>
                          Power: +12V {module.power_12v_ma ?? '—'}mA
                        </div>
                        {module.power_neg12v_ma ? (
                          <div>−12V {module.power_neg12v_ma}mA</div>
                        ) : null}
                      </div>
                    </div>
                    <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <Link className="button button-secondary" to="/racks/new">
                        Place on rig
                      </Link>
                      <Link className="button button-quiet" to="/racks">
                        Open rigs
                      </Link>
                    </div>
                  </article>
                </li>
              ))}
            </ul>
          )}
        </>
      ) : null}
    </section>
  );
}
