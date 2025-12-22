import { useEffect, useState } from 'react';
import { adminApi, moduleApi } from '@/lib/api';
import type { Module } from '@/types/api';
import { AdminGuard } from './AdminGuard';
import { AdminNav } from './AdminNav';

const STATUS_OPTIONS = ['active', 'deprecated', 'tombstoned'];

export default function AdminModules() {
  const [modules, setModules] = useState<Module[]>([]);
  const [reason, setReason] = useState('');
  const [mergeTarget, setMergeTarget] = useState<Record<number, number>>({});

  const fetchModules = async () => {
    const response = await moduleApi.list({ limit: 50 });
    setModules(response.data.modules);
  };

  useEffect(() => {
    fetchModules();
  }, []);

  return (
    <AdminGuard>
      <h2>Modules</h2>
      <AdminNav />
      <div style={{ marginBottom: '1rem' }}>
        <label>
          Audit reason:
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            style={{ marginLeft: '0.5rem', padding: '0.4rem' }}
          />
        </label>
      </div>
      <div style={{ display: 'grid', gap: '1rem' }}>
        {modules.map((module) => (
          <div key={module.id} style={{ border: '1px solid #333', padding: '1rem', borderRadius: '6px' }}>
            <strong>{module.brand}</strong> — {module.name}
            <div>Status: {module.status || 'active'}</div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
              <select
                onChange={async (e) => {
                  await adminApi.updateModuleStatus(module.id, e.target.value, reason || 'status update');
                  fetchModules();
                }}
                defaultValue={module.status || 'active'}
              >
                {STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
              <input
                type="number"
                placeholder="Replacement ID"
                value={mergeTarget[module.id] || ''}
                onChange={(e) =>
                  setMergeTarget((prev) => ({
                    ...prev,
                    [module.id]: Number(e.target.value),
                  }))
                }
                style={{ width: '140px' }}
              />
              <button
                onClick={async () => {
                  const replacementId = mergeTarget[module.id];
                  if (!replacementId) return;
                  await adminApi.mergeModule(module.id, replacementId, reason || 'merge');
                  fetchModules();
                }}
              >
                Merge
              </button>
            </div>
          </div>
        ))}
      </div>
    </AdminGuard>
  );
}
