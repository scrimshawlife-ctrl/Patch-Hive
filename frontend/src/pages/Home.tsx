/**
 * Home — PatchHive product landing (Cyber Hive / Zero State).
 */
import { Link } from 'react-router-dom';
import { useAuthStore } from '@/lib/store';

const features = [
  {
    code: 'LIB',
    title: 'Module & case library',
    description:
      'Browse confirmed module and case specs. Missing technical data stays missing — never invented.',
  },
  {
    code: 'IN',
    title: 'Manual, photo, or hybrid intake',
    description:
      'Build a rig manually or review photo evidence. Provider detections stay untrusted until you confirm them.',
  },
  {
    code: 'GEN',
    title: 'Deterministic generation',
    description:
      'Reproduce patches constrained to your confirmed inventory revision. Absent hardware yields NOT_COMPUTABLE.',
  },
  {
    code: 'PB',
    title: 'PatchBooks & Style Studio',
    description:
      'Export provenance-bound PDF, SVG, JSON, or ZIP. Design Engine recipes restyle presentation only.',
  },
] as const;

const laws = [
  'Vision output is evidence only — never silent inventory truth',
  'Immutable rig revisions and deterministic generation seeds',
  'Signal types (audio / CV / gate) describe ports and cables, not DSP',
  'Credits debit only at the canonical export boundary',
] as const;

export default function Home() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return (
    <section aria-labelledby="home-title">
      <header className="page-hero">
        <p className="eyebrow">PatchHive · Zero State</p>
        <h1 id="home-title">Confirm the rig. Compile the signal. Export the book.</h1>
        <p className="page-hero-lede">
          Modular synthesizer patch documentation without audio simulation, hardware control, or
          invented inventory. Every export is bound to a run, seed, and content hash.
        </p>
        <div className="page-hero-actions">
          {isAuthenticated() ? (
            <Link className="button button-primary" to="/racks">
              Open rigs
            </Link>
          ) : (
            <Link className="button button-primary" to="/login">
              Sign in
            </Link>
          )}
          <Link className="button button-secondary" to="/modules?hp=known">
            Placeable modules
          </Link>
          <Link className="button button-secondary" to="/cases?format=eurorack">
            Eurorack cases
          </Link>
          <Link className="button button-quiet" to="/racks/new">
            New rig
          </Link>
        </div>
      </header>

      <div className="feature-grid" style={{ marginBottom: 'var(--space-6)' }}>
        {features.map((feature) => (
          <article key={feature.code} className="feature-card">
            <span className="feature-card-icon" aria-hidden="true">
              {feature.code}
            </span>
            <h2>{feature.title}</h2>
            <p>{feature.description}</p>
          </article>
        ))}
      </div>

      <div className="panel">
        <p className="eyebrow">Product law</p>
        <h2 style={{ marginTop: 0 }}>Boundaries that stay hard</h2>
        <ul className="auth-brand-list" style={{ marginTop: 'var(--space-4)' }}>
          {laws.map((law) => (
            <li key={law}>{law}</li>
          ))}
        </ul>
        <p className="muted" style={{ marginTop: 'var(--space-5)', marginBottom: 0 }}>
          Designed and engineered by Zero State · PatchHive product surface
        </p>
      </div>
    </section>
  );
}
