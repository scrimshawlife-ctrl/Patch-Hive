/**
 * Home page - Introduction to PatchHive.
 */
export default function Home() {
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '3rem', color: '#00ff88', marginBottom: '1rem' }}>
        Welcome to PatchHive
      </h1>
      <p style={{ fontSize: '1.25rem', color: '#ccc', marginBottom: '2rem' }}>
        Confirm a modular rig, generate hardware-constrained patches, and publish
        one-page Patch Books — without audio simulation or hardware control.
      </p>

      <div style={{ display: 'grid', gap: '2rem', marginTop: '3rem' }}>
        <Section
          title="Module & Case Library"
          description="Browse the confirmed module gallery and cases. Missing technical data stays missing."
        />
        <Section
          title="Manual, Photo, or Hybrid Intake"
          description="Build a rig manually or review photo evidence. Provider detections stay untrusted until you confirm them."
        />
        <Section
          title="Deterministic Patch Generation"
          description="Generate reproducible patches constrained to your confirmed inventory revision. Absent hardware yields NOT_COMPUTABLE, not invented gear."
        />
        <Section
          title="Patch Books & Export"
          description="Compile ordered cable diagrams and export PDF, SVG, JSON, or ZIP with provenance. Symbolic waveform thumbnails are visualization only."
        />
      </div>

      <div
        style={{
          marginTop: '3rem',
          padding: '1.5rem',
          background: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '8px',
        }}
      >
        <h2 style={{ color: '#00ff88', marginBottom: '1rem' }}>Product boundaries</h2>
        <ul style={{ color: '#ccc', lineHeight: '1.8' }}>
          <li>Vision output is evidence only — never silent inventory truth</li>
          <li>Immutable rig revisions and deterministic generation seeds</li>
          <li>Signal types such as audio/CV/gate describe ports and cables, not DSP</li>
          <li>Community social surfaces remain feature-flagged off by default</li>
        </ul>
      </div>
    </div>
  );
}

function Section({ title, description }: { title: string; description: string }) {
  return (
    <div
      style={{
        padding: '1.5rem',
        background: '#1a1a1a',
        border: '1px solid #333',
        borderRadius: '8px',
      }}
    >
      <h3 style={{ color: '#00ff88', marginBottom: '0.5rem' }}>{title}</h3>
      <p style={{ color: '#ccc', margin: 0 }}>{description}</p>
    </div>
  );
}
