/**
 * Public Product Database Explorer (PDB)
 * Manufacturer directory + search + basic detail.
 */
import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { registryApi } from '@/lib/api';
import type { Manufacturer, RegistryCoverage } from '@/types/api';

interface SelectedMan extends Manufacturer {
  models?: any[];
}

export default function RegistryPage() {
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);
  const [coverage, setCoverage] = useState<RegistryCoverage | null>(null);
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(() => searchParams.get('query') || searchParams.get('q') || '');
  const [selected, setSelected] = useState<SelectedMan | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchResults, setSearchResults] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      registryApi.listManufacturers({ limit: 200 }),
      registryApi.getCoverage(),
    ])
      .then(([mans, cov]) => {
        const items = (mans.data.items || mans.data || []).slice(0, 200);
        setManufacturers(items);
        setCoverage(cov.data);
      })
      .catch(console.error)
      .finally(() => {
        setLoading(false);
        const initialQ = searchParams.get('query') || searchParams.get('q');
        if (initialQ) {
          // filter will pick it up; optionally auto-select first match later
        }
      });
  }, []);

  const filtered = manufacturers.filter(m =>
    !query || m.name?.toLowerCase().includes(query.toLowerCase()) || m.slug?.toLowerCase().includes(query.toLowerCase())
  );

  const onSearch = async (q: string) => {
    if (!q) { setSearchResults([]); return; }
    try {
      const res = await registryApi.search(q, 8);  // assume updated
      setSearchResults(res.data.results || []);
    } catch (e) {
      setSearchResults([]);
    }
  };

  const selectMan = async (m: any) => {
    try {
      const res = await fetch(`/api/registry/manufacturers/${m.slug}`);
      const detail = await res.json();
      const modelsRes = await fetch(`/api/registry/manufacturers/${m.slug}/models`);
      const modelsData = await modelsRes.json();
      setSelected({ ...detail, models: modelsData.models || [] });
    } catch (e) {
      setSelected({ ...m, models: [] });
    }
  };

  if (loading) return <div className="p-8">Loading Product Database…</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex items-baseline justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Product Database</h1>
          <p className="text-sm text-gray-400">Live from registry • {coverage?.total_manufacturers || manufacturers.length} manufacturers • {coverage?.total_models || 0} models</p>
        </div>
        <input
          className="input w-72"
          placeholder="Search manufacturers or models…"
          value={query}
          onChange={e => {
            setQuery(e.target.value);
            onSearch(e.target.value);
          }}
        />
      </div>

      {searchResults.length > 0 && (
        <div className="mb-6 p-4 bg-zinc-900 rounded">
          <div className="text-xs uppercase tracking-widest mb-2 text-gray-400">Model search results</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {searchResults.map((r, i) => (
              <div key={i} className="text-sm border border-zinc-800 p-2 rounded">{r.brand} — {r.name} {r.hp ? `(${r.hp}hp)` : ''}</div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Directory */}
        <div className="lg:col-span-2">
          <div className="text-xs uppercase mb-2 tracking-widest text-gray-400">Manufacturers</div>
          <div className="border border-zinc-800 rounded divide-y divide-zinc-800 max-h-[520px] overflow-auto">
            {filtered.length === 0 && <div className="p-4 text-gray-400">No matches.</div>}
            {filtered.map(m => (
              <button
                key={m.slug || m.id}
                onClick={() => selectMan(m)}
                className="w-full text-left p-3 hover:bg-zinc-900 flex justify-between items-center"
              >
                <span className="font-medium">{m.name}</span>
                <span className="text-xs text-gray-500 font-mono">{m.slug}</span>
              </button>
            ))}
          </div>
          <div className="text-[10px] mt-2 text-gray-500">Showing {filtered.length} of {manufacturers.length}. Full search &amp; details coming.</div>
        </div>

        {/* Detail */}
        <div className="border border-zinc-800 rounded p-4 min-h-[200px]">
          {!selected ? (
            <div className="text-gray-400 text-sm">Select a manufacturer to see details (live DB data).</div>
          ) : (
            <>
              <div className="text-xl font-semibold mb-1">{selected.name}</div>
              <div className="text-xs text-gray-500 mb-4 font-mono">{selected.slug}</div>

              <div className="text-sm space-y-1">
                <div>Status: <span className="font-mono">{selected.status || 'active'}</span></div>
                {selected.website && <div>Website: <a href={selected.website} className="underline" target="_blank" rel="noreferrer">{selected.website}</a></div>}
              </div>

              <div className="mt-4 space-y-3">
                <div>
                  <div className="text-xs uppercase tracking-widest text-gray-400 mb-1">Registry Link</div>
                  <div className="text-sm font-mono">{selected.slug} {selected.id ? `(id ${selected.id})` : ""}</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-widest text-gray-400 mb-1">Models (sample)</div>
                  {(selected.models || []).slice(0,5).map((mod: any, i: number) => (
                    <div key={i} className="text-xs py-0.5">{mod.name} {mod.hp ? `(${mod.hp}hp)` : ''}</div>
                  ))}
                  {(!selected.models || selected.models.length === 0) && <div className="text-xs text-gray-500">No models loaded for this man yet.</div>}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
