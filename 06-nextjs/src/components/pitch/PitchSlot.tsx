'use client';
import React, { useState } from 'react';
import { Shirt } from './Shirt';
import { StatusOverlay } from './StatusOverlay';
import { GwColumn } from './GwColumn';
import { useTheme } from '@/contexts/ThemeContext';
import { EnrichedPlayer } from '@/lib/enrichment';
import { PlayerResponse, FixtureResponse } from '@/lib/api';

const DIFF_COLORS: Record<number, string> = {
  1: '#16a34a', 2: '#4ade80', 3: '#facc15', 4: '#f97316', 5: '#dc2626',
};

export type PlayerWithLocked = PlayerResponse & { locked: boolean };

type GwColData = {
  label: string;
  xp: number | null;
  fixtures: { opponent?: string; isHome?: boolean | null; difficulty?: number | null }[];
};

interface PitchSlotProps {
  player?: PlayerWithLocked | EnrichedPlayer | null;
  position: string;
  onSlotClick?: () => void;
  onRemove?: () => void;
  onLock?: () => void;
  resultsMode: boolean;
  transferIn?: boolean;
  transferOut?: boolean;
  gwCols?: GwColData[];
  clubOverCap?: boolean;
}

const SLOT_SIZE = 54;

function isEnriched(p: PlayerWithLocked | EnrichedPlayer): p is EnrichedPlayer {
  return 'is_starter' in p;
}

function isLocked(p: PlayerWithLocked | EnrichedPlayer): boolean {
  if ('locked' in p) return (p as PlayerWithLocked).locked;
  return false;
}

export function PitchSlot({
  player,
  position,
  onSlotClick,
  onRemove,
  onLock,
  resultsMode,
  transferIn,
  transferOut,
  gwCols = [],
  clubOverCap = false,
}: PitchSlotProps) {
  const theme = useTheme();
  const [hovered, setHovered] = useState(false);

  const slotWidth = resultsMode
    ? Math.max(SLOT_SIZE + 20, gwCols.length * 34 + 16)
    : SLOT_SIZE + 20;

  if (!player) {
    // Empty slot
    if (resultsMode) return null;
    return (
      <div
        onClick={onSlotClick}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          width: slotWidth,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 4,
          cursor: 'pointer',
        }}
      >
        <div style={{
          width: SLOT_SIZE,
          height: SLOT_SIZE,
          borderRadius: 8,
          border: `2px dashed ${hovered ? theme.accent : 'rgba(255,255,255,0.3)'}`,
          background: hovered ? `${theme.accent}18` : 'rgba(255,255,255,0.05)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'border-color 0.15s, background 0.15s',
        }}>
          <span style={{ fontSize: 20, color: hovered ? theme.accent : 'rgba(255,255,255,0.35)', lineHeight: 1 }}>+</span>
        </div>
        <div style={{
          fontSize: 9,
          fontWeight: 700,
          letterSpacing: '0.1em',
          color: 'rgba(255,255,255,0.4)',
          fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
        }}>
          {position}
        </div>
      </div>
    );
  }

  const locked = isLocked(player);
  const status = 'status' in player ? (player as PlayerResponse).status : undefined;
  const captain = isEnriched(player) ? player.is_captain : false;
  const h1Fixtures: FixtureResponse[] = !resultsMode
    ? ((player as PlayerResponse).fixtures?.filter(f => f.horizon === 1) ?? [])
    : [];

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: slotWidth,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 3,
        position: 'relative',
        opacity: transferOut ? 0.45 : 1,
        transition: 'opacity 0.2s',
      }}
    >
      {/* Shirt + badges */}
      <div style={{ position: 'relative' }}>
        <Shirt
          club={player.club_short}
          position={player.position}
          transferIn={transferIn}
          captain={captain}
          size={SLOT_SIZE}
        />
        {/* Status overlay */}
        <div style={{ position: 'absolute', bottom: -2, right: -2 }}>
          <StatusOverlay status={status}/>
        </div>
        {/* Lock badge - only in setup mode */}
        {!resultsMode && locked && (
          <div style={{
            position: 'absolute',
            bottom: -3,
            left: -3,
            width: 14,
            height: 14,
            borderRadius: '50%',
            background: '#d97706',
            border: '1.5px solid rgba(255,255,255,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 5,
          }}>
            <svg width="7" height="8" viewBox="0 0 24 24" fill="#fff">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
            </svg>
          </div>
        )}
        {/* Club cap warning badge */}
        {!resultsMode && clubOverCap && (
          <div style={{
            position: 'absolute',
            top: -4,
            left: -4,
            width: 14,
            height: 14,
            borderRadius: '50%',
            background: '#f59e0b',
            border: '1.5px solid rgba(255,255,255,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 6,
            fontSize: 8,
            fontWeight: 700,
            color: '#fff',
          }}>!</div>
        )}
        {/* Hover action buttons in setup mode */}
        {!resultsMode && hovered && (
          <div style={{
            position: 'absolute',
            top: -6,
            right: -6,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            zIndex: 10,
          }}>
            <button
              onClick={(e) => { e.stopPropagation(); onRemove?.(); }}
              style={{
                width: 16, height: 16, borderRadius: '50%',
                background: '#dc2626',
                border: 'none', cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 8, color: '#fff', fontWeight: 700,
                boxShadow: '0 1px 3px rgba(0,0,0,0.4)',
              }}
            >✕</button>
            <button
              onClick={(e) => { e.stopPropagation(); onLock?.(); }}
              style={{
                width: 16, height: 16, borderRadius: '50%',
                background: locked ? '#d97706' : 'rgba(0,0,0,0.5)',
                border: '1px solid rgba(255,255,255,0.3)',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 1px 3px rgba(0,0,0,0.4)',
              }}
            >
              <svg width="8" height="9" viewBox="0 0 24 24" fill="#fff">
                <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Player name */}
      <div style={{
        fontSize: 9,
        fontWeight: 600,
        color: 'rgba(255,255,255,0.9)',
        textAlign: 'center',
        maxWidth: slotWidth - 4,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        lineHeight: 1.2,
      }}>
        {player.name.split(' ').slice(-1)[0]}
      </div>

      {/* Price - setup mode only */}
      {!resultsMode && (
        <div style={{
          fontSize: 8,
          color: 'rgba(255,255,255,0.5)',
          fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
        }}>
          £{player.price.toFixed(1)}
        </div>
      )}

      {/* Fixture pips - setup mode only; shows both for DGW */}
      {!resultsMode && h1Fixtures.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
          {h1Fixtures.map((fix, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <div style={{
                width: 5, height: 5, borderRadius: '50%', flexShrink: 0,
                background: fix.difficulty != null
                  ? (DIFF_COLORS[fix.difficulty] ?? '#9ca3af')
                  : '#9ca3af',
              }}/>
              <span style={{ fontSize: 7, color: 'rgba(255,255,255,0.5)', whiteSpace: 'nowrap' }}>
                {fix.opponent}{fix.is_home != null ? (fix.is_home ? 'H' : 'A') : ''}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* GW columns - results mode only */}
      {resultsMode && gwCols.length > 0 && (
        <div style={{ display: 'flex', gap: 3, justifyContent: 'center' }}>
          {gwCols.map((col, i) => (
            <GwColumn
              key={i}
              gwLabel={col.label}
              xp={col.xp}
              fixtures={col.fixtures}
            />
          ))}
        </div>
      )}
    </div>
  );
}
