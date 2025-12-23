/**
 * Main App component with routing.
 */
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useAuthStore } from '@/lib/store';

// Pages
import Home from '@/pages/Home';
import ModulesPage from '@/pages/Modules';
import CasesPage from '@/pages/Cases';
import RacksPage from '@/pages/Racks';
import RackBuilderPage from '@/pages/RackBuilder';
import PatchesPage from '@/pages/Patches';
import FeedPage from '@/pages/Feed';
import LoginPage from '@/pages/Login';
import RigDetailPage from '@/pages/RigDetail';
import AdminDashboard from '@/pages/admin/AdminDashboard';
import AdminUsers from '@/pages/admin/AdminUsers';
import AdminModules from '@/pages/admin/AdminModules';
import AdminGallery from '@/pages/admin/AdminGallery';
import AdminRuns from '@/pages/admin/AdminRuns';
import AdminExports from '@/pages/admin/AdminExports';
import AdminLeaderboards from '@/pages/admin/AdminLeaderboards';
import AccountPage from '@/pages/Account';
import PublishPage from '@/pages/Publish';
import GalleryPage from '@/pages/Gallery';
import PublicationPage from '@/pages/Publication';
import LeaderboardsModulesPage from '@/pages/LeaderboardsModules';

function App() {
  const { user, logout, isAuthenticated } = useAuthStore();
  const canSeeAdmin = user && ['Admin', 'Ops', 'Support', 'ReadOnly'].includes(user.role);

  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', backgroundColor: '#0a0a0a', color: '#fff' }}>
        {/* Header */}
        <header
          style={{
            borderBottom: '1px solid #333',
            padding: '1rem 2rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
            <h1 style={{ margin: 0, fontSize: '1.5rem', color: '#00ff88' }}>
              <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                PatchHive
              </Link>
            </h1>
            <nav style={{ display: 'flex', gap: '1rem' }}>
              <NavLink to="/modules">Modules</NavLink>
              <NavLink to="/cases">Cases</NavLink>
              <NavLink to="/racks">Rigs</NavLink>
              <NavLink to="/patches">Patches</NavLink>
              <NavLink to="/feed">Feed</NavLink>
              <NavLink to="/gallery">Gallery</NavLink>
              <NavLink to="/publish">Publish</NavLink>
              <NavLink to="/leaderboards/modules">Leaderboards</NavLink>
              {isAuthenticated() && <NavLink to="/account">Account</NavLink>}
              {canSeeAdmin ? <NavLink to="/admin">Admin</NavLink> : null}
            </nav>
          </div>
          <div>
            {isAuthenticated() ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span>{user?.username}</span>
                <button
                  onClick={logout}
                  style={{
                    background: '#333',
                    color: '#fff',
                    border: '1px solid #555',
                    padding: '0.5rem 1rem',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link to="/login">
                <button
                  style={{
                    background: '#00ff88',
                    color: '#000',
                    border: 'none',
                    padding: '0.5rem 1rem',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                  }}
                >
                  Login
                </button>
              </Link>
            )}
          </div>
        </header>

        {/* Main Content */}
        <main style={{ padding: '2rem' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/modules" element={<ModulesPage />} />
            <Route path="/cases" element={<CasesPage />} />
            <Route path="/racks" element={<RacksPage />} />
            <Route path="/racks/new" element={<RackBuilderPage />} />
            <Route path="/racks/:id/edit" element={<RackBuilderPage />} />
            <Route path="/rigs/:rigId" element={<RigDetailPage />} />
            <Route path="/patches" element={<PatchesPage />} />
            <Route path="/feed" element={<FeedPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/gallery" element={<GalleryPage />} />
            <Route path="/publish" element={<PublishPage />} />
            <Route path="/account" element={<AccountPage />} />
            <Route path="/p/:slug" element={<PublicationPage />} />
            <Route path="/leaderboards/modules" element={<LeaderboardsModulesPage />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/modules" element={<AdminModules />} />
            <Route path="/admin/gallery" element={<AdminGallery />} />
            <Route path="/admin/runs" element={<AdminRuns />} />
            <Route path="/admin/exports" element={<AdminExports />} />
            <Route path="/admin/leaderboards" element={<AdminLeaderboards />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer
          style={{
            borderTop: '1px solid #333',
            padding: '1rem 2rem',
            textAlign: 'center',
            color: '#666',
            fontSize: '0.875rem',
          }}
        >
          <p>PatchHive v0.1.0 - Built with ABX-Core v1.2 principles</p>
          <p>Deterministic patch generation with full provenance tracking</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      style={{
        color: '#ccc',
        textDecoration: 'none',
        padding: '0.5rem 1rem',
        borderRadius: '4px',
        transition: 'background 0.2s',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = '#222';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'transparent';
      }}
    >
      {children}
    </Link>
  );
}

export default App;
