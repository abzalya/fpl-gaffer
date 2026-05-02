'use client';
import { useTheme } from '@/contexts/ThemeContext';

interface AboutModalProps {
  onClose: () => void;
}

export function AboutModal({ onClose }: AboutModalProps) {
  const t = useTheme();

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 200,
        background: t.isLight ? 'rgba(0,0,0,0.3)' : 'rgba(0,0,0,0.6)',
        backdropFilter: 'blur(4px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          width: 440,
          borderRadius: 14,
          background: t.isLight ? '#faf7f2' : '#13151a',
          border: `1px solid ${t.border}`,
          boxShadow: t.isLight ? '0 24px 80px rgba(0,0,0,0.12)' : '0 24px 80px rgba(0,0,0,0.55)',
          overflow: 'hidden',
        }}
      >
        {/* Header bar */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '16px 20px',
          borderBottom: `1px solid ${t.border}`,
        }}>
          <span style={{
            fontSize: 14, fontWeight: 800, letterSpacing: '-0.03em',
            color: t.text1,
            fontFamily: 'var(--font-dm-sans), system-ui, sans-serif',
          }}>
            fpl-<span style={{ color: t.accent }}>gaffer</span>
          </span>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: t.text3, fontSize: 18, lineHeight: 1, padding: 2,
            }}
          >✕</button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px 20px 24px' }}>
          <p style={{
            fontSize: 13, lineHeight: 1.65, color: t.text2,
            fontFamily: 'var(--font-dm-sans), system-ui, sans-serif',
            marginBottom: 20,
          }}>
            FPL Gaffer is a squad optimiser for Fantasy Premier League. It uses linear
            programming to suggest the best transfers for your squad across a configurable
            planning horizon — balancing expected points, budget, and free transfers.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[
              { label: 'Solver', value: 'PuLP · CBC (COIN-BC)' },
              { label: 'Data', value: 'FPL API + ML predicted points' },
              { label: 'Stack', value: 'Next.js · FastAPI · dbt · PostgreSQL' },
            ].map(({ label, value }) => (
              <div key={label} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
                padding: '8px 12px', borderRadius: 7,
                background: t.bg1, border: `1px solid ${t.border2}`,
              }}>
                <span style={{ fontSize: 11, color: t.text3, fontFamily: 'var(--font-dm-mono), DM Mono, monospace', letterSpacing: '0.05em' }}>
                  {label}
                </span>
                <span style={{ fontSize: 11, fontWeight: 600, color: t.text1, fontFamily: 'var(--font-dm-mono), DM Mono, monospace' }}>
                  {value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
