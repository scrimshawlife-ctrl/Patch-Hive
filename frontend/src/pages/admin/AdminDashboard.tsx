import { AdminGuard } from './AdminGuard';
import { AdminNav } from './AdminNav';

export default function AdminDashboard() {
  return (
    <AdminGuard>
      <div>
        <h2>Admin Console</h2>
        <AdminNav />
        <div style={{ border: '1px solid #333', padding: '1rem', borderRadius: '6px' }}>
          <p>Use the console to manage users, modules, gallery revisions, runs, exports, and leaderboards.</p>
          <ul>
            <li>All admin mutations are audited.</li>
            <li>Credits changes are appended to the ledger.</li>
            <li>Modules are deprecated or tombstoned (no hard deletes).</li>
          </ul>
        </div>
      </div>
    </AdminGuard>
  );
}
