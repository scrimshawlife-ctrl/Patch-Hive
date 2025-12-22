import { useState } from 'react';
import { adminApi } from '@/lib/api';
import { AdminGuard } from './AdminGuard';
import { AdminNav } from './AdminNav';

export default function AdminExports() {
  const [exportId, setExportId] = useState('');
  const [cacheRunId, setCacheRunId] = useState('');
  const [cacheExportType, setCacheExportType] = useState('');
  const [reason, setReason] = useState('');

  return (
    <AdminGuard>
      <h2>Exports</h2>
      <AdminNav />
      <div style={{ border: '1px solid #333', padding: '1rem', marginBottom: '1rem' }}>
        <div style={{ marginBottom: '0.5rem' }}>
          <label>
            Audit reason:
            <input
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              style={{ marginLeft: '0.5rem', padding: '0.4rem' }}
            />
          </label>
        </div>
        <input
          value={exportId}
          onChange={(e) => setExportId(e.target.value)}
          placeholder="Export ID"
          style={{ marginRight: '0.5rem', padding: '0.4rem' }}
        />
        <button
          onClick={async () => {
            if (!exportId) return;
            await adminApi.unlockExport(Number(exportId), reason || 'unlock');
          }}
        >
          Unlock
        </button>
        <button
          onClick={async () => {
            if (!exportId) return;
            await adminApi.revokeExport(Number(exportId), reason || 'revoke');
          }}
          style={{ marginLeft: '0.5rem' }}
        >
          Revoke
        </button>
      </div>
      <div style={{ border: '1px solid #333', padding: '1rem' }}>
        <h3>Cache Invalidate</h3>
        <input
          value={cacheRunId}
          onChange={(e) => setCacheRunId(e.target.value)}
          placeholder="Run ID"
          style={{ marginRight: '0.5rem', padding: '0.4rem' }}
        />
        <input
          value={cacheExportType}
          onChange={(e) => setCacheExportType(e.target.value)}
          placeholder="Export type"
          style={{ marginRight: '0.5rem', padding: '0.4rem' }}
        />
        <button
          onClick={async () => {
            await adminApi.invalidateCache({
              run_id: cacheRunId ? Number(cacheRunId) : undefined,
              export_type: cacheExportType || undefined,
              reason: reason || 'cache invalidate',
            });
          }}
        >
          Invalidate
        </button>
      </div>
    </AdminGuard>
  );
}
