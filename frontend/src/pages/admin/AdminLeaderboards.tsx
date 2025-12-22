import { useEffect, useState } from 'react';
import { adminApi } from '@/lib/api';
import type { AdminLeaderboardEntry } from '@/types/admin';
import { AdminGuard } from './AdminGuard';
import { AdminNav } from './AdminNav';

export default function AdminLeaderboards() {
  const [popular, setPopular] = useState<AdminLeaderboardEntry[]>([]);
  const [trending, setTrending] = useState<AdminLeaderboardEntry[]>([]);
  const [exported, setExported] = useState<AdminLeaderboardEntry[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const [popularRes, trendingRes, exportedRes] = await Promise.all([
        adminApi.popularModules(),
        adminApi.trendingModules(14),
        adminApi.exportedCategories(),
      ]);
      setPopular(popularRes.data);
      setTrending(trendingRes.data);
      setExported(exportedRes.data);
    };
    fetchData();
  }, []);

  return (
    <AdminGuard>
      <h2>Leaderboards</h2>
      <AdminNav />
      <section style={{ marginBottom: '1.5rem' }}>
        <h3>Popular Modules</h3>
        <ul>
          {popular.map((entry) => (
            <li key={entry.label}>
              {entry.label} — {entry.count}
            </li>
          ))}
        </ul>
      </section>
      <section style={{ marginBottom: '1.5rem' }}>
        <h3>Trending Modules (14 days)</h3>
        <ul>
          {trending.map((entry) => (
            <li key={entry.label}>
              {entry.label} — {entry.count}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h3>Exported Categories</h3>
        <ul>
          {exported.map((entry) => (
            <li key={entry.label}>
              {entry.label} — {entry.count}
            </li>
          ))}
        </ul>
      </section>
    </AdminGuard>
  );
}
