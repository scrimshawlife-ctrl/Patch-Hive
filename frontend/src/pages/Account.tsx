import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { publishingApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import type { PublicationRecord } from '@/types/api';

interface PublicationDraft {
  title: string;
  description: string;
}

export default function AccountPage() {
  const { isAuthenticated } = useAuthStore();
  const [publications, setPublications] = useState<PublicationRecord[]>([]);
  const [drafts, setDrafts] = useState<Record<number, PublicationDraft>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPublications = async () => {
    setLoading(true);
    try {
      const response = await publishingApi.listPublications();
      setPublications(response.data.publications);
      const nextDrafts: Record<number, PublicationDraft> = {};
      response.data.publications.forEach((pub) => {
        nextDrafts[pub.id] = {
          title: pub.title,
          description: pub.description || '',
        };
      });
      setDrafts(nextDrafts);
      setError(null);
    } catch (err) {
      setError('Unable to load publications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated()) {
      fetchPublications();
    }
  }, [isAuthenticated]);

  const updatePublication = async (id: number, updates: Partial<PublicationRecord>) => {
    try {
      await publishingApi.updatePublication(id, updates);
      fetchPublications();
    } catch (err) {
      setError('Unable to update publication.');
    }
  };

  const saveDraft = async (id: number) => {
    const draft = drafts[id];
    if (!draft) return;
    await updatePublication(id, {
      title: draft.title,
      description: draft.description,
    });
  };

  if (!isAuthenticated()) {
    return <p>Please log in to manage publishing.</p>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <section
        style={{
          background: '#111',
          border: '1px solid #222',
          borderRadius: '8px',
          padding: '1.5rem',
        }}
      >
        <h2 style={{ marginTop: 0 }}>Publishing</h2>
        <p style={{ color: '#aaa' }}>
          Manage published exports and keep visibility aligned with your intent.
        </p>
        <Link to="/publish">
          <button
            style={{
              background: '#00ff88',
              color: '#000',
              border: 'none',
              padding: '0.6rem 1.2rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold',
            }}
          >
            Publish an export
          </button>
        </Link>
      </section>

      <section
        style={{
          background: '#111',
          border: '1px solid #222',
          borderRadius: '8px',
          padding: '1.5rem',
        }}
      >
        <h3 style={{ marginTop: 0 }}>Your publications</h3>
        {loading && <p>Loading publications...</p>}
        {error && <p style={{ color: '#ff6b6b' }}>{error}</p>}
        {!loading && publications.length === 0 && (
          <p style={{ color: '#aaa' }}>No publications yet.</p>
        )}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {publications.map((publication) => (
            <div
              key={publication.id}
              style={{
                border: '1px solid #222',
                padding: '1rem',
                borderRadius: '8px',
                background: '#0d0d0d',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <input
                    value={drafts[publication.id]?.title || ''}
                    onChange={(event) =>
                      setDrafts((prev) => ({
                        ...prev,
                        [publication.id]: {
                          title: event.target.value,
                          description: prev[publication.id]?.description || '',
                        },
                      }))
                    }
                    style={{
                      width: '100%',
                      padding: '0.4rem 0.6rem',
                      borderRadius: '4px',
                      border: '1px solid #333',
                      background: '#111',
                      color: '#fff',
                      fontSize: '1rem',
                    }}
                  />
                  <textarea
                    value={drafts[publication.id]?.description || ''}
                    onChange={(event) =>
                      setDrafts((prev) => ({
                        ...prev,
                        [publication.id]: {
                          title: prev[publication.id]?.title || '',
                          description: event.target.value,
                        },
                      }))
                    }
                    rows={2}
                    style={{
                      width: '100%',
                      marginTop: '0.5rem',
                      padding: '0.4rem 0.6rem',
                      borderRadius: '4px',
                      border: '1px solid #333',
                      background: '#111',
                      color: '#ccc',
                    }}
                  />
                  <p style={{ margin: '0.4rem 0 0', color: '#666' }}>
                    Slug: /p/{publication.slug}
                  </p>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label style={{ color: '#ccc' }}>
                    Visibility
                    <select
                      value={publication.visibility}
                      onChange={(event) =>
                        updatePublication(publication.id, {
                          visibility: event.target.value as PublicationRecord['visibility'],
                        })
                      }
                      style={{
                        marginLeft: '0.5rem',
                        background: '#111',
                        color: '#fff',
                        border: '1px solid #333',
                        borderRadius: '4px',
                      }}
                    >
                      <option value="unlisted">Unlisted</option>
                      <option value="public">Public</option>
                    </select>
                  </label>
                  <label style={{ color: '#ccc' }}>
                    Allow download
                    <input
                      type="checkbox"
                      checked={publication.allow_download}
                      onChange={(event) =>
                        updatePublication(publication.id, { allow_download: event.target.checked })
                      }
                      style={{ marginLeft: '0.5rem' }}
                    />
                  </label>
                  <button
                    onClick={() =>
                      updatePublication(publication.id, {
                        status: publication.status === 'hidden' ? 'published' : 'hidden',
                      })
                    }
                    style={{
                      background: '#222',
                      color: '#fff',
                      border: '1px solid #333',
                      padding: '0.4rem 0.8rem',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    {publication.status === 'hidden' ? 'Unhide' : 'Hide'}
                  </button>
                  <button
                    onClick={() => saveDraft(publication.id)}
                    style={{
                      background: '#00ff88',
                      color: '#000',
                      border: 'none',
                      padding: '0.4rem 0.8rem',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                    }}
                  >
                    Save
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
