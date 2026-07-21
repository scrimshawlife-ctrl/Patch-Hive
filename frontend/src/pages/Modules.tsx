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
        <div className="header-actions">
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
          <div className="panel" aria-label="Module filters" style={{ marginBottom: 'var(--space-4)' }}>
            <div className="toolbar">
              <label className="field" htmlFor="module-search" style={{ flex: '1 1 12rem' }}>
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
              <label className="inline-field" htmlFor="module-brand">
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
              <label className="inline-field" htmlFor="module-type">
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
              <label className="inline-field" htmlFor="module-sort">
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
              {filtersActive ? (
                <button className="button button-quiet" type="button" onClick={clearFilters}>
                  Clear filters
                </button>
              ) : null}
            </div>
          </div>

          <p className="muted" role="status" style={{ marginBottom: 'var(--space-4)' }}>
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
            <ul className="catalog-grid" aria-label="Module catalog results">
              {filtered.map((module) => (
                <li key={module.id}>
                  <article className="catalog-card" style={{ height: '100%' }}>
                    <span className="feature-card-icon" aria-hidden="true">
                      {module.hp}H
                    </span>
                    <h2>
                      {module.brand} — {module.name}
                    </h2>
                    <p className="catalog-card-meta">
                      {module.module_type} · {module.hp}HP
                    </p>
                    {module.description ? (
                      <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        {module.description}
                      </p>
                    ) : null}
                    <p className="catalog-card-meta">
                      +12V {module.power_12v_ma ?? '—'}mA
                      {module.power_neg12v_ma != null ? ` · −12V ${module.power_neg12v_ma}mA` : ''}
                    </p>
                    <div className="page-hero-actions">
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
