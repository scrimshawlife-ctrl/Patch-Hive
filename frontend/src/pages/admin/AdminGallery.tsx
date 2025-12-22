import { useEffect, useState } from 'react';
import { adminApi } from '@/lib/api';
import type { AdminGalleryRevision } from '@/types/admin';
import { AdminGuard } from './AdminGuard';
import { AdminNav } from './AdminNav';

export default function AdminGallery() {
  const [revisions, setRevisions] = useState<AdminGalleryRevision[]>([]);

  const fetchRevisions = async () => {
    const response = await adminApi.listGalleryRevisions();
    setRevisions(response.data.revisions);
  };

  useEffect(() => {
    fetchRevisions();
  }, []);

  return (
    <AdminGuard>
      <h2>Gallery Revisions</h2>
      <AdminNav />
      <div style={{ display: 'grid', gap: '1rem' }}>
        {revisions.map((revision) => (
          <div key={revision.id} style={{ border: '1px solid #333', padding: '1rem' }}>
            <div>
              <strong>{revision.module_key}</strong> — {revision.revision_id}
            </div>
            <div>Status: {revision.status}</div>
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
              <button
                onClick={async () => {
                  await adminApi.approveRevision(revision.id);
                  fetchRevisions();
                }}
              >
                Approve
              </button>
              <button
                onClick={async () => {
                  await adminApi.confirmRevision(revision.id);
                  fetchRevisions();
                }}
              >
                Confirm
              </button>
            </div>
          </div>
        ))}
      </div>
    </AdminGuard>
  );
}
