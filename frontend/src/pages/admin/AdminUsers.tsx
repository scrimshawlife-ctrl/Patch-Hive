import { useEffect, useState } from 'react';
import { adminApi } from '@/lib/api';
import type { AdminUser } from '@/types/admin';
import { AdminGuard } from './AdminGuard';
import { AdminNav } from './AdminNav';

const ROLE_OPTIONS = ['Admin', 'Ops', 'Support', 'ReadOnly', 'User'];

export default function AdminUsers() {
  const [query, setQuery] = useState('');
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [reasonByUser, setReasonByUser] = useState<Record<number, string>>({});

  const fetchUsers = async () => {
    const response = await adminApi.listUsers(query || undefined);
    setUsers(response.data.users);
  };

  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AdminGuard>
      <h2>Users</h2>
      <AdminNav />
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search users"
          style={{ padding: '0.5rem', minWidth: '240px' }}
        />
        <button onClick={fetchUsers}>Search</button>
      </div>
      <div style={{ display: 'grid', gap: '1rem' }}>
        {users.map((user) => (
          <div key={user.id} style={{ border: '1px solid #333', padding: '1rem', borderRadius: '6px' }}>
            <strong>{user.username}</strong> ({user.email})<br />
            Role: {user.role} | Display: {user.display_name || '—'}
            <div style={{ marginTop: '0.75rem' }}>
              <label>
                Audit reason:
                <input
                  value={reasonByUser[user.id] || ''}
                  onChange={(e) =>
                    setReasonByUser((prev) => ({ ...prev, [user.id]: e.target.value }))
                  }
                  style={{ marginLeft: '0.5rem', padding: '0.4rem' }}
                />
              </label>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
              <select
                value={user.role}
                onChange={async (e) => {
                  const reason = reasonByUser[user.id] || 'role update';
                  await adminApi.updateUserRole(user.id, e.target.value, reason);
                  fetchUsers();
                }}
              >
                {ROLE_OPTIONS.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
              <button
                onClick={async () => {
                  const reason = reasonByUser[user.id] || 'grant credits';
                  await adminApi.grantCredits(user.id, 3, reason);
                  fetchUsers();
                }}
              >
                Grant 3 credits
              </button>
              <button
                onClick={async () => {
                  const reason = reasonByUser[user.id] || 'clear avatar';
                  await adminApi.updateUserAvatar(user.id, null, reason);
                  fetchUsers();
                }}
              >
                Clear avatar
              </button>
            </div>
          </div>
        ))}
      </div>
    </AdminGuard>
  );
}
