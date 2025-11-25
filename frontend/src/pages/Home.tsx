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
        Design, catalog, share, and explore Eurorack systems and their possible patches.
      </p>

      <div style={{ display: 'grid', gap: '2rem', marginTop: '3rem' }}>
        <Section
          title="Module & Case Library"
          description="Browse and manage a comprehensive library of Eurorack modules and cases. Import from ModularGrid or add manually."
        />
        <Section
          title="Rack Builder"
          description="Design your dream Eurorack system with validation for HP, power draw, and layout constraints."
        />
        <Section
          title="Deterministic Patch Generation"
          description="Generate plausible patch configurations using our ABX-Core compliant engine. Each patch is reproducible from its seed."
        />
        <Section
          title="Visualization & Export"
          description="View rack layouts, patch diagrams, and waveform approximations. Export to PDF for your patch book."
        />
        <Section
          title="Community Sharing"
          description="Share your racks and patches publicly. Browse the feed, vote, and comment on community creations."
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
        <h2 style={{ color: '#00ff88', marginBottom: '1rem' }}>ABX-Core v1.2 Principles</h2>
        <ul style={{ color: '#ccc', lineHeight: '1.8' }}>
          <li>Modular, deterministic, entropy-minimizing architecture</li>
          <li>SEED enforcement: Full provenance and data lineage tracking</li>
          <li>Eurorack mental model: modules, cases, patches, and signals</li>
          <li>No mock data beyond minimal, clearly-labeled seeds for testing</li>
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
