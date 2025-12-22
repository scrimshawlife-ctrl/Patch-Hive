import { useAuthStore } from '@/lib/store';

const READ_ROLES = new Set(['Admin', 'Ops', 'Support', 'ReadOnly']);

export function AdminGuard({ children }: { children: React.ReactNode }) {
  const { user } = useAuthStore();

  if (!user || !READ_ROLES.has(user.role)) {
    return (
      <div style={{ padding: '2rem', border: '1px solid #333' }}>
        <h2 style={{ color: '#ff6666' }}>Admin access required</h2>
        <p>Contact an administrator to request access.</p>
      </div>
    );
  }

  return <>{children}</>;
}
