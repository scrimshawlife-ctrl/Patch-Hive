/**
 * User dashboard page for credits, exports, referrals, and profile.
 */
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { accountApi, authApi, exportApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import type { CreditsSummary, ExportRecord, ReferralSummary, User } from '@/types/api';

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
  const [exports, setExports] = useState<ExportRecord[]>([]);
  const [referrals, setReferrals] = useState<ReferralSummary | null>(null);
  const [profile, setProfile] = useState<User | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');
  const [saving, setSaving] = useState(false);
  const [copyStatus, setCopyStatus] = useState('');

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    const loadDashboard = async () => {
      const [creditsRes, exportsRes, referralsRes, profileRes] = await Promise.all([
        accountApi.getCredits(),
        accountApi.getExports(),
        accountApi.getReferrals(),
        authApi.getMe(),
      ]);
      setCredits(creditsRes.data);
      setExports(exportsRes.data);
      setReferrals(referralsRes.data);
      setProfile(profileRes.data);
      setDisplayName(profileRes.data.display_name || profileRes.data.username);
      setAvatarUrl(profileRes.data.avatar_url || '');
      setAuth(profileRes.data, localStorage.getItem('auth_token') || '');
    };

    if (isAuthenticated()) {
      loadDashboard();
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
    return exports.map((record) => {
      const isPatch = record.export_type === 'patch';
      const label = isPatch ? 'Patch' : 'Rack';
      const downloadLink = record.unlocked
        ? isPatch
          ? exportApi.patchPdf(record.entity_id)
          : exportApi.rackPdf(record.entity_id)
        : null;
      return { ...record, label, downloadLink };
    });
  }, [exports]);

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
        PatchHive is free to explore. You only pay when you export something you want to keep.
      </p>

      <section style={sectionStyle}>
        <h3>Credits</h3>
        <p style={labelStyle}>Balance</p>
        <h2 style={{ marginTop: '0.25rem' }}>{credits ? credits.balance : '—'}</h2>
        <p style={{ ...labelStyle, marginTop: '1rem' }}>History</p>
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
                <tr key={entry.id} style={{ borderTop: '1px solid #222' }}>
                  <td style={{ padding: '0.5rem' }}>{entry.entry_type}</td>
                  <td style={{ padding: '0.5rem' }}>{entry.amount}</td>
                  <td style={{ padding: '0.5rem' }}>{new Date(entry.created_at).toLocaleString()}</td>
                  <td style={{ padding: '0.5rem', color: '#888' }}>{entry.description || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#777' }}>No credit history yet.</p>
        )}
      </section>

      <section style={sectionStyle}>
        <h3>Exports</h3>
        {exportRows.length ? (
          <table style={{ width: '100%', marginTop: '0.5rem', borderCollapse: 'collapse' }}>
            <thead style={{ textAlign: 'left', color: '#888' }}>
              <tr>
                <th style={{ padding: '0.5rem' }}>Type</th>
                <th style={{ padding: '0.5rem' }}>Run ID</th>
                <th style={{ padding: '0.5rem' }}>Date</th>
                <th style={{ padding: '0.5rem' }}>License</th>
                <th style={{ padding: '0.5rem' }}>Download</th>
              </tr>
            </thead>
            <tbody>
              {exportRows.map((record) => (
                <tr key={record.id} style={{ borderTop: '1px solid #222' }}>
                  <td style={{ padding: '0.5rem' }}>{record.label}</td>
                  <td style={{ padding: '0.5rem', color: '#888' }}>{record.run_id}</td>
                  <td style={{ padding: '0.5rem' }}>{new Date(record.created_at).toLocaleString()}</td>
                  <td style={{ padding: '0.5rem' }}>{record.license_type || '—'}</td>
                  <td style={{ padding: '0.5rem' }}>
                    {record.downloadLink ? (
                      <a
                        href={record.downloadLink}
                        style={{ color: '#00ff88', textDecoration: 'none' }}
                      >
                        Download
                      </a>
                    ) : (
                      <span style={{ color: '#666' }}>Locked</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#777' }}>No exports yet.</p>
        )}
      </section>

      <section style={sectionStyle}>
        <h3>Referrals</h3>
        <p style={{ color: '#bbb' }}>
          You’ll receive free credits if your friend makes their first purchase.
        </p>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginTop: '1rem' }}>
          <input
            type="text"
            value={referrals?.referral_link || ''}
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
            <h3>{referrals?.pending_count ?? '—'}</h3>
          </div>
          <div>
            <p style={labelStyle}>Earned</p>
            <h3>{referrals?.earned_count ?? '—'}</h3>
          </div>
        </div>
        {referrals?.recent_referrals.length ? (
          <div style={{ marginTop: '1rem' }}>
            <p style={labelStyle}>Recent referrals</p>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {referrals.recent_referrals.map((referral, index) => (
                <li key={`${referral.referred_user_id}-${index}`} style={{ padding: '0.35rem 0' }}>
                  <span style={{ color: '#ccc' }}>{referral.referred_user_id}</span>
                  <span style={{ color: '#666', marginLeft: '0.5rem' }}>{referral.status}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p style={{ color: '#777', marginTop: '1rem' }}>No referrals yet.</p>
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
          <p style={{ color: '#666', marginTop: '0.75rem' }}>
            Signed in as {profile.username}
          </p>
        )}
      </section>
    </div>
  );
}
