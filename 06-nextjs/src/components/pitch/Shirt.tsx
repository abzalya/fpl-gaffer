'use client';
import React from 'react';
import { KIT_PATTERNS, FALLBACK_KIT } from './KitPatterns';

const OUTLINE = "M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z";

export function Shirt({ club, position, transferIn, captain, size = 54 }: {
  club?: string;
  position?: string;
  transferIn?: boolean;
  captain?: boolean;
  size?: number;
}) {
  const kit = KIT_PATTERNS[club ?? ''] ?? FALLBACK_KIT;
  const isGKP = position === 'GKP';
  const primary = isGKP ? kit.gkp : kit.p;
  const secondary = kit.s;
  const sc = Math.round(size * 0.88);

  return (
    <div style={{ position: 'relative', width: size, height: size, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {transferIn && (
        <div style={{
          position: 'absolute', inset: -4, borderRadius: 6,
          border: '2.5px solid #22c55e',
          boxShadow: '0 0 10px rgba(34,197,94,0.55)',
          zIndex: 1, pointerEvents: 'none'
        }}/>
      )}
      <svg
        width={sc}
        height={Math.round(sc * 1.1)}
        viewBox="0 0 50 56"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ position: 'relative', zIndex: 2, filter: 'drop-shadow(0 2px 3px rgba(0,0,0,0.3))' }}
      >
        {isGKP && <>
          <rect x="1" y="11" width="8" height="12" rx="2" fill={primary} stroke={secondary} strokeWidth="0.8"/>
          <rect x="41" y="11" width="8" height="12" rx="2" fill={primary} stroke={secondary} strokeWidth="0.8"/>
        </>}
        {kit.render(primary, secondary)}
        <path d={OUTLINE} fill="none" stroke="rgba(0,0,0,0.18)" strokeWidth="0.7"/>
      </svg>
      {captain && (
        <div style={{
          position: 'absolute', top: -3, right: -3,
          width: 17, height: 17, borderRadius: '50%',
          background: 'oklch(50% 0.22 290)',
          border: '2px solid rgba(0,0,0,0.3)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 8, fontWeight: 900, color: '#fff', fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
          zIndex: 6, boxShadow: '0 1px 4px rgba(0,0,0,0.4)'
        }}>C</div>
      )}
    </div>
  );
}
