import { Link } from 'react-router-dom';

const links = [
  { to: '/admin', label: 'Dashboard' },
  { to: '/admin/users', label: 'Users' },
  { to: '/admin/modules', label: 'Modules' },
  { to: '/admin/gallery', label: 'Gallery' },
  { to: '/admin/runs', label: 'Runs' },
  { to: '/admin/exports', label: 'Exports' },
  { to: '/admin/leaderboards', label: 'Leaderboards' },
];

export function AdminNav() {
  return (
    <nav style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
      {links.map((link) => (
        <Link
          key={link.to}
          to={link.to}
          style={{
            padding: '0.4rem 0.8rem',
            borderRadius: '4px',
            border: '1px solid #333',
            color: '#9fd',
            textDecoration: 'none',
          }}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
