/**
 * Module gallery — browse lightweight module_catalog (research + curated)
 * with optional materialize into full-spec inventory for rack placement.
 */
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { moduleApi } from '@/lib/api';
import type { CatalogModule, CatalogModuleStats } from '@/types/api';

type LoadState = 'loading' | 'ready' | 'empty' | 'error';
type SortKey = 'brand' | 'name' | 'hp' | 'category';
type HpFilter = 'all' | 'known' | 'unknown';

const PAGE_SIZE = 48;

export default function ModulesPage() {
  const [modules, setModules] = useState<CatalogModule[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<CatalogModuleStats | null>(null);
  const [brands, setBrands] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [state, setState] = useState<LoadState>('loading');
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [brandFilter, setBrandFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [hpFilter, setHpFilter] = useState<HpFilter>('all');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [availabilityFilter, setAvailabilityFilter] = useState('all');
  const [sortKey, setSortKey] = useState<SortKey>('brand');
  const [page, setPage] = useState(0);
  const [busySlug, setBusySlug] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState('');

  const load = useCallback(() => {
    setState('loading');
    setError('');
    setActionMsg('');
    const params: Record<string, string | number | boolean> = {
      skip: page * PAGE_SIZE,
      limit: PAGE_SIZE,
      sort_by: sortKey === 'category' ? 'category' : sortKey,
      sort_order: 'asc',
    };
    if (query.trim()) params.search = query.trim();
    if (brandFilter !== 'all') params.brand = brandFilter;
    if (typeFilter !== 'all') params.category = typeFilter;
    if (hpFilter === 'known') params.hp_known = true;
    if (hpFilter === 'unknown') params.hp_known = false;
    if (sourceFilter !== 'all') params.source = sourceFilter;
    if (availabilityFilter !== 'all') params.is_available = availabilityFilter;

    Promise.all([
      moduleApi.catalog(params),
      moduleApi.catalogStats(),
      moduleApi.catalogBrands(),
      moduleApi.catalogCategories(),
    ])
      .then(([listRes, statsRes, brandsRes, catsRes]) => {
        const rows = listRes.data.modules ?? [];
        setModules(rows);
        setTotal(listRes.data.total ?? 0);
        setStats(statsRes.data);
        setBrands((brandsRes.data.brands ?? []).map((b) => b.name));
        setCategories((catsRes.data.categories ?? []).map((c) => c.name).filter(Boolean));
        setState(listRes.data.total === 0 ? 'empty' : 'ready');
      })
      .catch(() => {
        setModules([]);
        setTotal(0);
        setError('Unable to load module catalog. Check that the API is reachable and try again.');
        setState('error');
      });
  }, [page, sortKey, query, brandFilter, typeFilter, hpFilter, sourceFilter, availabilityFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const clearFilters = () => {
    setQuery('');
    setBrandFilter('all');
    setTypeFilter('all');
    setHpFilter('all');
    setSourceFilter('all');
    setAvailabilityFilter('all');
    setSortKey('brand');
    setPage(0);
  };

  const filtersActive =
    query.trim() ||
    brandFilter !== 'all' ||
    typeFilter !== 'all' ||
    hpFilter !== 'all' ||
    sourceFilter !== 'all' ||
    availabilityFilter !== 'all';

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const placeFromCatalog = async (row: CatalogModule) => {
    setBusySlug(row.slug);
    setActionMsg('');
    try {
      if (row.hp == null) {
        setActionMsg(
          `${row.brand} ${row.name}: HP unknown — cannot place until manufacturer width is confirmed.`,
        );
        return;
      }
      const res = await moduleApi.materializeCatalog(row.slug);
      setActionMsg(
        `${res.data.module.brand} ${res.data.module.name} ready (module #${res.data.module_id}, ${res.data.status}). Open a rig to place it.`,
      );
    } catch {
      setActionMsg(
        `${row.brand} ${row.name}: materialize failed (needs known HP or API error).`,
      );
    } finally {
      setBusySlug(null);
    }
  };

  return (
    <section aria-labelledby="modules-title">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Catalog</p>
          <h1 id="modules-title">Module gallery</h1>
          <p className="muted">
            Browse the lightweight module catalog (research seed + curated). Full power/I/O specs
            load when you materialize a row with known HP for rack placement — unknown widths stay
            null (never invented).
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

      {stats ? (
        <div className="panel" style={{ marginBottom: 'var(--space-4)' }} aria-label="Catalog stats">
          <p className="muted" style={{ margin: 0 }}>
            <strong>{stats.total_modules}</strong> modules · <strong>{stats.total_brands}</strong>{' '}
            brands · HP known <strong>{stats.hp_stats.known}</strong> (
            {stats.hp_stats.coverage_pct}%) · unknown <strong>{stats.hp_stats.unknown}</strong> ·
            available <strong>{stats.availability.available}</strong>
            {stats.by_source
              ? ` · sources ${Object.entries(stats.by_source)
                  .map(([k, n]) => `${k || 'unknown'}=${n}`)
                  .join(', ')}`
              : ''}
          </p>
        </div>
      ) : null}

      {actionMsg ? (
        <p className="status" role="status" style={{ marginBottom: 'var(--space-4)' }}>
          {actionMsg}
        </p>
      ) : null}

      {state === 'loading' ? (
        <p className="status" role="status">
          Loading catalog…
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
          <p className="status status-warning">No modules in the catalog yet.</p>
          <p className="muted">
            Run synth catalog import or ModularGrid curated populate to seed discovery.
          </p>
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
                  placeholder="Brand, name…"
                  onChange={(event) => {
                    setPage(0);
                    setQuery(event.target.value);
                  }}
                  autoComplete="off"
                />
              </label>
              <label className="inline-field" htmlFor="module-brand">
                Brand
                <select
                  id="module-brand"
                  value={brandFilter}
                  onChange={(event) => {
                    setPage(0);
                    setBrandFilter(event.target.value);
                  }}
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
                Category
                <select
                  id="module-type"
                  value={typeFilter}
                  onChange={(event) => {
                    setPage(0);
                    setTypeFilter(event.target.value);
                  }}
                >
                  <option value="all">All categories</option>
                  {categories.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </label>
              <label className="inline-field" htmlFor="module-hp">
                HP
                <select
                  id="module-hp"
                  value={hpFilter}
                  onChange={(event) => {
                    setPage(0);
                    setHpFilter(event.target.value as HpFilter);
                  }}
                >
                  <option value="all">All</option>
                  <option value="known">Known width</option>
                  <option value="unknown">Unknown width</option>
                </select>
              </label>
              <label className="inline-field" htmlFor="module-source">
                Source
                <select
                  id="module-source"
                  value={sourceFilter}
                  onChange={(event) => {
                    setPage(0);
                    setSourceFilter(event.target.value);
                  }}
                >
                  <option value="all">All sources</option>
                  {stats?.by_source
                    ? Object.keys(stats.by_source)
                        .filter(Boolean)
                        .sort()
                        .map((src) => (
                          <option key={src} value={src}>
                            {src}
                          </option>
                        ))
                    : null}
                  {!stats?.by_source ? (
                    <option value="SynthCatalogResearch">SynthCatalogResearch</option>
                  ) : null}
                </select>
              </label>
              <label className="inline-field" htmlFor="module-availability">
                Status
                <select
                  id="module-availability"
                  value={availabilityFilter}
                  onChange={(event) => {
                    setPage(0);
                    setAvailabilityFilter(event.target.value);
                  }}
                >
                  <option value="all">All status</option>
                  <option value="available">available</option>
                  <option value="discontinued">discontinued</option>
                  <option value="upcoming">upcoming</option>
                  <option value="duplicate">duplicate</option>
                  <option value="non_eurorack">non_eurorack</option>
                  <option value="desktop">desktop</option>
                  <option value="unresolved">unresolved</option>
                </select>
              </label>
              <label className="inline-field" htmlFor="module-sort">
                Sort
                <select
                  id="module-sort"
                  value={sortKey}
                  onChange={(event) => {
                    setPage(0);
                    setSortKey(event.target.value as SortKey);
                  }}
                >
                  <option value="brand">Brand</option>
                  <option value="name">Name</option>
                  <option value="category">Category</option>
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
            Showing {modules.length} of {total} catalog modules
            {filtersActive ? ' (filtered)' : ''} · page {page + 1}/{totalPages}
          </p>

          {modules.length === 0 ? (
            <div className="panel">
              <p className="status status-warning">No modules match these filters.</p>
              <button className="button button-secondary" type="button" onClick={clearFilters}>
                Clear filters
              </button>
            </div>
          ) : (
            <ul className="catalog-grid" aria-label="Module catalog results">
              {modules.map((module) => (
                <li key={module.slug}>
                  <article className="catalog-card" style={{ height: '100%' }}>
                    <span className="feature-card-icon" aria-hidden="true">
                      {module.hp != null ? `${module.hp}H` : '—'}
                    </span>
                    <h2>
                      {module.brand} — {module.name}
                    </h2>
                    <p className="catalog-card-meta">
                      {module.category ?? 'UTIL'} ·{' '}
                      {module.hp != null ? (
                        <span title="Manufacturer-confirmed width">{module.hp}HP</span>
                      ) : (
                        <span title="Width not confirmed — not placeable">HP unknown</span>
                      )}
                      {module.hp != null ? (
                        <span className="muted" title="Catalog width is known">
                          {' '}
                          · placeable
                        </span>
                      ) : null}
                      {module.source ? ` · ${module.source}` : ''}
                      {module.is_available && module.is_available !== 'available'
                        ? ` · ${module.is_available}`
                        : ''}
                    </p>
                    <div className="page-hero-actions">
                      <button
                        className="button button-secondary"
                        type="button"
                        disabled={busySlug === module.slug || module.hp == null}
                        title={
                          module.hp == null
                            ? 'Needs manufacturer-confirmed HP before placement'
                            : 'Materialize full module record for rack placement'
                        }
                        onClick={() => placeFromCatalog(module)}
                      >
                        {busySlug === module.slug
                          ? 'Working…'
                          : module.hp == null
                            ? 'HP unknown'
                            : 'Prepare for rig'}
                      </button>
                      <Link className="button button-quiet" to="/racks">
                        Open rigs
                      </Link>
                    </div>
                  </article>
                </li>
              ))}
            </ul>
          )}

          {totalPages > 1 ? (
            <div className="toolbar" style={{ marginTop: 'var(--space-4)' }}>
              <button
                className="button button-secondary"
                type="button"
                disabled={page <= 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
              >
                Previous
              </button>
              <button
                className="button button-secondary"
                type="button"
                disabled={page + 1 >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
