/**
 * User dashboard: canonical credits/exports + optional referrals + profile.
 */
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { accountApi, authApi, canonApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import type { CreditsSummary, UserExportRecord, ReferralSummary, User } from '@/types/api';

const sectionStyle: React.CSSProperties = {
  background: '#111',
  border: '1px solid #222',
  borderRadius: '8px',
  padding: '1.5rem',
  marginBottom: '1.5rem',
};

const labelStyle: React.CSSProperties = {
  color: '#aaa',
  fontSize: '0.9rem',
};

export default function AccountPage() {
  const navigate = useNavigate();
  const { isAuthenticated, setAuth } = useAuthStore();
  const [credits, setCredits] = useState<CreditsSummary | null>(null);
  const [exports, setExports] = useState<UserExportRecord[]>([]);
  const [referrals, setReferrals] = useState<ReferralSummary | null>(null);
  const [profile, setProfile] = useState<User | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');
  const [saving, setSaving] = useState(false);
  const [copyStatus, setCopyStatus] = useState('');
  const [tokenBusy, setTokenBusy] = useState<string | null>(null);
  const [tokenMessage, setTokenMessage] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const loadDashboard = async () => {
      const [creditsRes, exportsRes, profileRes] = await Promise.all([
        accountApi.getCredits(),
        accountApi.getExports(),
        authApi.getMe(),
      ]);
      setCredits(creditsRes.data);
      setExports(exportsRes.data as UserExportRecord[]);
      setProfile(profileRes.data);
      setDisplayName(profileRes.data.display_name || profileRes.data.username);
      setAvatarUrl(profileRes.data.avatar_url || '');
      setAuth(profileRes.data, localStorage.getItem('auth_token') || '');

      try {
        const referralsRes = await accountApi.getReferrals();
        setReferrals(referralsRes.data);
      } catch {
        setReferrals(null);
      }
    };

    if (isAuthenticated()) {
      loadDashboard().catch(() => {
        /* keep empty dashboard on failure */
      });
    }
  }, [isAuthenticated, setAuth]);

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      const res = await authApi.updateProfile({
        display_name: displayName,
        avatar_url: avatarUrl || undefined,
      });
      setProfile(res.data);
      setAuth(res.data, localStorage.getItem('auth_token') || '');
    } finally {
      setSaving(false);
    }
  };

  const exportRows = useMemo(() => {
    return exports.map((record) => ({
      ...record,
      label: record.source === 'canon' ? 'Canonical export' : record.export_type,
      canRequestToken: Boolean(record.unlocked && record.source === 'canon'),
    }));
  }, [exports]);

  const handleDownloadToken = async (exportId: string) => {
    setTokenBusy(exportId);
    setTokenMessage('');
    try {
      const res = await canonApi.createDownloadToken(exportId, 300);
      setTokenMessage(`Download token issued for ${exportId} (TTL ${res.data.ttl_seconds}s).`);
    } catch (error: unknown) {
      const apiError = error as { response?: { data?: { detail?: string } } };
      setTokenMessage(apiError.response?.data?.detail || 'Could not issue download token.');
    } finally {
      setTokenBusy(null);
    }
  };

  const handleCopy = async () => {
    if (!referrals?.referral_link) return;
    await navigator.clipboard.writeText(referrals.referral_link);
    setCopyStatus('Copied');
    setTimeout(() => setCopyStatus(''), 2000);
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '0.5rem' }}>Account</h2>
      <p style={{ color: '#bbb', marginBottom: '2rem' }}>
        PatchHive is free to explore. Credits and export debits use the canonical ledger (
        <code>/api/canon/*</code>).
      </p>

      <section style={sectionStyle}>
        <h3>Credits</h3>
        <p style={labelStyle}>Canonical balance</p>
        <h2 style={{ marginTop: '0.25rem' }}>{credits ? credits.balance : '—'}</h2>
        <p style={{ ...labelStyle, marginTop: '1rem' }}>Ledger history</p>
        {credits?.entries.length ? (
          <table style={{ width: '100%', marginTop: '0.5rem', borderCollapse: 'collapse' }}>
            <thead style={{ textAlign: 'left', color: '#888' }}>
              <tr>
                <th style={{ padding: '0.5rem' }}>Type</th>
                <th style={{ padding: '0.5rem' }}>Amount</th>
                <th style={{ padding: '0.5rem' }}>Date</th>
                <th style={{ padding: '0.5rem' }}>Note</th>
              </tr>
            </thead>
            <tbody>
              {credits.entries.map((entry) => (
                <tr key={String(entry.id)} style={{ borderTop: '1px solid #222' }}>
                  <td style={{ padding: '0.5rem' }}>{entry.entry_type}</td>
                  <td style={{ padding: '0.5rem' }}>{entry.amount}</td>
                  <td style={{ padding: '0.5rem' }}>{new Date(entry.created_at).toLocaleString()}</td>
                  <td style={{ padding: '0.5rem', color: '#888' }}>{entry.description || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#777' }}>No canonical credit history yet.</p>
        )}
      </section>

      <section style={sectionStyle}>
        <h3>Exports</h3>
        {tokenMessage ? <p style={{ color: '#00ff88' }}>{tokenMessage}</p> : null}
        {exportRows.length ? (
          <table style={{ width: '100%', marginTop: '0.5rem', borderCollapse: 'collapse' }}>
            <thead style={{ textAlign: 'left', color: '#888' }}>
              <tr>
                <th style={{ padding: '0.5rem' }}>Type</th>
                <th style={{ padding: '0.5rem' }}>Run ID</th>
                <th style={{ padding: '0.5rem' }}>Status</th>
                <th style={{ padding: '0.5rem' }}>Date</th>
                <th style={{ padding: '0.5rem' }}>Download</th>
              </tr>
            </thead>
            <tbody>
              {exportRows.map((record) => (
                <tr key={String(record.id)} style={{ borderTop: '1px solid #222' }}>
                  <td style={{ padding: '0.5rem' }}>{record.label}</td>
                  <td style={{ padding: '0.5rem', color: '#888' }}>{record.run_id}</td>
                  <td style={{ padding: '0.5rem' }}>{record.status || '—'}</td>
                  <td style={{ padding: '0.5rem' }}>{new Date(record.created_at).toLocaleString()}</td>
                  <td style={{ padding: '0.5rem' }}>
                    {record.canRequestToken ? (
                      <button
                        type="button"
                        onClick={() => handleDownloadToken(String(record.id))}
                        disabled={tokenBusy === String(record.id)}
                        style={{
                          background: 'transparent',
                          border: '1px solid #00ff88',
                          color: '#00ff88',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          cursor: 'pointer',
                        }}
                      >
                        {tokenBusy === String(record.id) ? 'Issuing…' : 'Issue token'}
                      </button>
                    ) : (
                      <span style={{ color: '#666' }}>{record.unlocked ? 'Ready' : 'Locked'}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#777' }}>No canonical exports yet.</p>
        )}
      </section>

      <section style={sectionStyle}>
        <h3>Referrals</h3>
        {referrals ? (
          <>
            <p style={{ color: '#bbb' }}>
              You’ll receive free credits if your friend makes their first purchase.
            </p>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginTop: '1rem' }}>
              <input
                type="text"
                value={referrals.referral_link || ''}
                readOnly
                style={{
                  flex: 1,
                  background: '#0c0c0c',
                  border: '1px solid #333',
                  color: '#ccc',
                  padding: '0.5rem',
                  borderRadius: '4px',
                }}
              />
              <button
                onClick={handleCopy}
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
                Invite a friend
              </button>
              {copyStatus && <span style={{ color: '#00ff88' }}>{copyStatus}</span>}
            </div>
            <div style={{ display: 'flex', gap: '2rem', marginTop: '1rem' }}>
              <div>
                <p style={labelStyle}>Pending</p>
                <h3>{referrals.pending_count ?? '—'}</h3>
              </div>
              <div>
                <p style={labelStyle}>Earned</p>
                <h3>{referrals.earned_count ?? '—'}</h3>
              </div>
            </div>
          </>
        ) : (
          <p style={{ color: '#777' }}>
            Referrals are feature-flagged off in the default MVP (`ENABLE_LEGACY_REFERRALS=false`).
          </p>
        )}
      </section>

      <section style={sectionStyle}>
        <h3>Profile</h3>
        <div style={{ display: 'grid', gap: '1rem', maxWidth: '400px' }}>
          <label>
            <div style={labelStyle}>Display name</div>
            <input
              type="text"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              style={{
                width: '100%',
                background: '#0c0c0c',
                border: '1px solid #333',
                color: '#ccc',
                padding: '0.5rem',
                borderRadius: '4px',
              }}
            />
          </label>
          <label>
            <div style={labelStyle}>Avatar URL</div>
            <input
              type="url"
              value={avatarUrl}
              onChange={(event) => setAvatarUrl(event.target.value)}
              placeholder="https://"
              style={{
                width: '100%',
                background: '#0c0c0c',
                border: '1px solid #333',
                color: '#ccc',
                padding: '0.5rem',
                borderRadius: '4px',
              }}
            />
          </label>
          {avatarUrl && (
            <img
              src={avatarUrl}
              alt="Avatar preview"
              style={{ width: '96px', height: '96px', borderRadius: '50%' }}
            />
          )}
          <button
            onClick={handleSaveProfile}
            disabled={saving}
            style={{
              background: '#333',
              color: '#fff',
              border: '1px solid #555',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            {saving ? 'Saving...' : 'Save profile'}
          </button>
        </div>
        {profile && (
          <p style={{ color: '#666', marginTop: '0.75rem' }}>Signed in as {profile.username}</p>
        )}
      </section>
    </div>
  );
}
