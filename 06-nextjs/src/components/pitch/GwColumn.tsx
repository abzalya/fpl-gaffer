'use client';
import React from 'react';

function DiffPip({ difficulty }: { difficulty: number | null }) {
  const colors: Record<number, string> = {
    1: '#16a34a',
    2: '#4ade80',
    3: '#facc15',
    4: '#f97316',
    5: '#dc2626',
  };
  const color = difficulty != null ? (colors[difficulty] ?? '#9ca3af') : '#9ca3af';
  return (
    <div style={{
      width: 6,
      height: 6,
      borderRadius: '50%',
      background: color,
      flexShrink: 0,
    }}/>
  );
}

export function GwColumn({ gwLabel, xp, opponent, isHome, difficulty }: {
  gwLabel: string;
  xp: number | null;
  opponent?: string;
  isHome?: boolean | null;
  difficulty?: number | null;
}) {
  const xpVal = xp ?? 0;
  let xpBg = 'rgba(0,0,0,0.15)';
  let xpColor = 'rgba(255,255,255,0.5)';
  if (xpVal >= 7) {
    xpBg = 'rgba(34,197,94,0.25)';
    xpColor = '#4ade80';
  } else if (xpVal >= 5) {
    xpBg = 'rgba(250,204,21,0.15)';
    xpColor = '#fbbf24';
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 2,
      minWidth: 32,
    }}>
      <div style={{
        fontSize: 7,
        fontWeight: 700,
        color: 'rgba(255,255,255,0.45)',
        fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
        letterSpacing: '0.05em',
      }}>
        {gwLabel}
      </div>
      <div style={{
        padding: '1px 4px',
        borderRadius: 4,
        background: xpBg,
        fontSize: 8,
        fontWeight: 700,
        color: xpColor,
        fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
        minWidth: 24,
        textAlign: 'center',
      }}>
        {xpVal.toFixed(1)}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <DiffPip difficulty={difficulty ?? null}/>
        {opponent && (
          <span style={{
            fontSize: 6,
            color: 'rgba(255,255,255,0.5)',
            fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
            textTransform: 'uppercase',
          }}>
            {opponent}{isHome != null ? (isHome ? 'H' : 'A') : ''}
          </span>
        )}
      </div>
    </div>
  );
}
