import { useEffect, useState } from 'react';
import { adminApi } from '@/lib/api';
import type { AdminRun } from '@/types/admin';
import { AdminGuard } from './AdminGuard';
import { AdminNav } from './AdminNav';

export default function AdminRuns() {
  const [runs, setRuns] = useState<AdminRun[]>([]);
  const [rerunRigId, setRerunRigId] = useState('');

  const fetchRuns = async () => {
    const response = await adminApi.listRuns();
    setRuns(response.data.runs);
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  return (
    <AdminGuard>
      <h2>Runs</h2>
      <AdminNav />
      <div style={{ marginBottom: '1rem' }}>
        <input
          value={rerunRigId}
          onChange={(e) => setRerunRigId(e.target.value)}
          placeholder="Rig ID to rerun"
          style={{ marginRight: '0.5rem', padding: '0.4rem' }}
        />
        <button
          onClick={async () => {
            if (!rerunRigId) return;
            await adminApi.rerunRig(Number(rerunRigId));
            setRerunRigId('');
            fetchRuns();
          }}
        >
          Rerun
        </button>
      </div>
      <div style={{ display: 'grid', gap: '1rem' }}>
        {runs.map((run) => (
          <div key={run.id} style={{ border: '1px solid #333', padding: '1rem' }}>
            Run #{run.id} — Rack {run.rack_id} — {run.status}
          </div>
        ))}
      </div>
    </AdminGuard>
  );
}
