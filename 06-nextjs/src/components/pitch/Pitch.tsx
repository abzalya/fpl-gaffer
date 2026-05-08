'use client';
import React from 'react';
import { PitchSlot, PlayerWithLocked } from './PitchSlot';
import { EnrichedPlayer } from '@/lib/enrichment';
import { TransferResponse } from '@/lib/api';

const PITCH_W = 660;
const PITCH_H = 620;

type PitchPlayer = PlayerWithLocked | EnrichedPlayer;

interface PitchProps {
  squad: PitchPlayer[];
  onSlotClick?: (pos: string) => void;
  onRemovePlayer?: (player: PitchPlayer) => void;
  onLockPlayer?: (player: PitchPlayer) => void;
  resultsMode: boolean;
  transfersIn?: TransferResponse[];
  transfersOut?: TransferResponse[];
  horizon?: number;
  clubCounts?: Record<string, number>;
}

const SETUP_COUNTS: Record<string, number> = { GKP: 2, DEF: 5, MID: 5, FWD: 3 };
const POSITION_ORDER = ['GKP', 'DEF', 'MID', 'FWD'];

function PitchMarkings() {
  return (
    <svg
      width={PITCH_W}
      height={PITCH_H}
      viewBox={`0 0 ${PITCH_W} ${PITCH_H}`}
      style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}
    >
      {/* Grass stripes */}
      {Array.from({ length: 7 }).map((_, i) => (
        <rect
          key={i}
          x={0} y={i * 89} width={PITCH_W} height={44.5}
          fill={i % 2 === 0 ? 'rgba(0,0,0,0.04)' : 'transparent'}
        />
      ))}
      {/* Boundary */}
      <rect x={20} y={14} width={PITCH_W - 40} height={PITCH_H - 28} rx={4} fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth={1.5}/>
      {/* Centre line */}
      <line x1={20} y1={PITCH_H / 2} x2={PITCH_W - 20} y2={PITCH_H / 2} stroke="rgba(255,255,255,0.18)" strokeWidth={1.2}/>
      {/* Centre circle */}
      <circle cx={PITCH_W / 2} cy={PITCH_H / 2} r={52} fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth={1.2}/>
      {/* Centre dot */}
      <circle cx={PITCH_W / 2} cy={PITCH_H / 2} r={3} fill="rgba(255,255,255,0.25)"/>
      {/* Top penalty box */}
      <rect x={(PITCH_W - 220) / 2} y={14} width={220} height={80} fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth={1}/>
      {/* Top six-yard box */}
      <rect x={(PITCH_W - 100) / 2} y={14} width={100} height={30} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth={1}/>
      {/* Bottom penalty box */}
      <rect x={(PITCH_W - 220) / 2} y={PITCH_H - 94} width={220} height={80} fill="none" stroke="rgba(255,255,255,0.14)" strokeWidth={1}/>
      {/* Bottom six-yard box */}
      <rect x={(PITCH_W - 100) / 2} y={PITCH_H - 44} width={100} height={30} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth={1}/>
      {/* Corner arcs */}
      <path d="M20 14 Q28 14 28 22" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth={1}/>
      <path d="M640 14 Q632 14 632 22" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth={1}/>
      <path d="M20 606 Q28 606 28 598" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth={1}/>
      <path d="M640 606 Q632 606 632 598" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth={1}/>
    </svg>
  );
}

export function Pitch({
  squad,
  onSlotClick,
  onRemovePlayer,
  onLockPlayer,
  resultsMode,
  transfersIn = [],
  transfersOut = [],
  horizon = 1,
  clubCounts = {},
}: PitchProps) {
  const transferInCodes = new Set(transfersIn.map(t => t.opta_code));
  const transferOutCodes = new Set(transfersOut.map(t => t.opta_code));

  // Build rows
  let rows: { position: string; players: (PitchPlayer | null)[] }[];
  let benchPlayers: PitchPlayer[] = [];

  if (!resultsMode) {
    rows = POSITION_ORDER.map(pos => {
      const filled = squad.filter(p => p.position === pos);
      const count = SETUP_COUNTS[pos] ?? 0;
      const slots: (PitchPlayer | null)[] = [...filled];
      while (slots.length < count) slots.push(null);
      return { position: pos, players: slots };
    });
  } else {
    const starters = squad.filter(p => {
      const ep = p as EnrichedPlayer;
      return ep.is_starter !== false;
    });
    benchPlayers = squad.filter(p => {
      const ep = p as EnrichedPlayer;
      return ep.is_starter === false;
    });

    const byPos: Record<string, PitchPlayer[]> = {};
    for (const p of starters) {
      if (!byPos[p.position]) byPos[p.position] = [];
      byPos[p.position].push(p);
    }
    rows = POSITION_ORDER.filter(pos => (byPos[pos]?.length ?? 0) > 0).map(pos => ({
      position: pos,
      players: byPos[pos],
    }));
  }

  // Build GW cols for a player in results mode
  function getGwCols(player: PitchPlayer) {
    const ep = player as EnrichedPlayer;
    if (!ep.expected_pts) return [];
    return ep.expected_pts.slice(0, horizon).map((pt, i) => {
      const fixes = ep.fixtures?.filter(f => f.horizon === i + 1) ?? [];
      return {
        label: `GW${pt.gw}`,
        xp: pt.pts,
        fixtures: fixes.map(f => ({ opponent: f.opponent, isHome: f.is_home, difficulty: f.difficulty })),
      };
    });
  }

  return (
    <div style={{
      position: 'relative',
      width: PITCH_W,
      minHeight: PITCH_H,
      borderRadius: 10,
      overflow: 'visible',
      background: 'linear-gradient(180deg, #2d6a3a 0%, #256132 50%, #2d6a3a 100%)',
    }}>
      <PitchMarkings/>

      {/* Player rows */}
      <div style={{
        position: 'relative',
        zIndex: 2,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-evenly',
        padding: '12px 0 14px',
        minHeight: PITCH_H,
      }}>
        {rows.map(({ position, players }) => (
          <div key={position} style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 4,
          }}>
            <div style={{
              fontSize: 8,
              letterSpacing: '0.14em',
              fontWeight: 700,
              color: 'rgba(255,255,255,0.35)',
              fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
            }}>
              {position}
            </div>
            <div style={{
              display: 'flex',
              gap: resultsMode ? 6 : 8,
              justifyContent: 'center',
              flexWrap: 'nowrap',
            }}>
              {players.map((player, idx) => (
                <PitchSlot
                  key={player ? player.opta_code : `empty-${position}-${idx}`}
                  player={player}
                  position={position}
                  onSlotClick={player ? undefined : () => onSlotClick?.(position)}
                  onRemove={player ? () => onRemovePlayer?.(player) : undefined}
                  onLock={player ? () => onLockPlayer?.(player) : undefined}
                  resultsMode={resultsMode}
                  transferIn={player ? transferInCodes.has(player.opta_code) : false}
                  transferOut={player ? transferOutCodes.has(player.opta_code) : false}
                  gwCols={player && resultsMode ? getGwCols(player) : []}
                  clubOverCap={player ? (clubCounts[player.club_short] ?? 0) > 3 : false}
                />
              ))}
            </div>
          </div>
        ))}

        {/* Bench - results mode only */}
        {resultsMode && benchPlayers.length > 0 && (
          <>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '6px 20px',
              margin: '4px 0',
            }}>
              <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.15)' }}/>
              <span style={{
                fontSize: 8,
                letterSpacing: '0.14em',
                fontWeight: 700,
                color: 'rgba(255,255,255,0.35)',
                fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
              }}>BENCH</span>
              <div style={{ flex: 1, height: 1, background: 'rgba(255,255,255,0.15)' }}/>
            </div>
            <div style={{
              display: 'flex',
              gap: resultsMode ? 6 : 8,
              justifyContent: 'center',
              opacity: 0.65,
            }}>
              {benchPlayers.map((player) => (
                <PitchSlot
                  key={player.opta_code}
                  player={player}
                  position={player.position}
                  resultsMode={resultsMode}
                  transferIn={transferInCodes.has(player.opta_code)}
                  transferOut={transferOutCodes.has(player.opta_code)}
                  gwCols={getGwCols(player)}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
