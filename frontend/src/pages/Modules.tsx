/**
 * Module Library page - Browse and manage modules.
 */
import { useState, useEffect } from 'react';
import { moduleApi } from '@/lib/api';
import type { Module } from '@/types/api';

export default function ModulesPage() {
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    moduleApi
      .list()
      .then((res) => {
        setModules(res.data.modules);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading modules...</div>;

  return (
    <div>
      <h1 style={{ fontSize: '2rem', marginBottom: '2rem' }}>Module Library</h1>

      <div style={{ marginBottom: '2rem' }}>
        <p style={{ color: '#ccc' }}>Total modules: {modules.length}</p>
      </div>

      <div style={{ display: 'grid', gap: '1rem' }}>
        {modules.map((module) => (
          <div
            key={module.id}
            style={{
              padding: '1rem',
              background: '#1a1a1a',
              border: '1px solid #333',
              borderRadius: '4px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div>
                <h3 style={{ color: '#00ff88', marginBottom: '0.5rem' }}>
                  {module.brand} - {module.name}
                </h3>
                <p style={{ color: '#ccc', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                  {module.module_type} | {module.hp}HP
                </p>
                {module.description && (
                  <p style={{ color: '#888', fontSize: '0.875rem' }}>{module.description}</p>
                )}
              </div>
              <div style={{ textAlign: 'right', color: '#666', fontSize: '0.75rem' }}>
                <div>Power: +12V {module.power_12v_ma}mA</div>
                {module.power_neg12v_ma && <div>-12V {module.power_neg12v_ma}mA</div>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
