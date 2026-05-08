'use client';
import React, { useState, useMemo } from 'react';
import { PlayerResponse } from '@/lib/api';
import { useTheme } from '@/contexts/ThemeContext';

type SortKey = 'predicted_pts_h1' | 'predicted_pts_h2' | 'predicted_pts_h3' | 'price';

const POSITION_COLORS: Record<string, string> = {
  GKP: '#f59e0b',
  DEF: '#3b82f6',
  MID: '#22c55e',
  FWD: '#ef4444',
};

const DIFF_COLORS: Record<number, string> = {
  1: '#16a34a',
  2: '#4ade80',
  3: '#facc15',
  4: '#f97316',
  5: '#dc2626',
};

interface PlayerPickerProps {
  filterPosition: string | null;
  currentSquad: PlayerResponse[];
  allPlayers: PlayerResponse[];
  clubCounts?: Record<string, number>;
  onSelect: (player: PlayerResponse) => void;
  onClose: () => void;
}

export function PlayerPicker({ filterPosition, currentSquad, allPlayers, clubCounts = {}, onSelect, onClose }: PlayerPickerProps) {
  const theme = useTheme();
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('predicted_pts_h1');

  const squadCodes = new Set(currentSquad.map(p => p.opta_code));

  const filtered = useMemo(() => {
    let list = allPlayers.filter(p => {
      if (squadCodes.has(p.opta_code)) return false;
      if (filterPosition && p.position !== filterPosition) return false;
      if (p.status === 'i' || p.status === 's' || p.status === 'u') return false;
      if (search) {
        const q = search.toLowerCase();
        return p.name.toLowerCase().includes(q) || p.club.toLowerCase().includes(q) || p.club_short.toLowerCase().includes(q);
      }
      return true;
    });

    list = [...list].sort((a, b) => {
      if (sortKey === 'price') return b.price - a.price;
      const av = a[sortKey] ?? 0;
      const bv = b[sortKey] ?? 0;
      return bv - av;
    });

    return list;
  }, [allPlayers, filterPosition, search, sortKey, squadCodes]);

  const sortOptions: { key: SortKey; label: string }[] = [
    { key: 'predicted_pts_h1', label: 'xP GW+1' },
    { key: 'predicted_pts_h2', label: 'xP GW+2' },
    { key: 'predicted_pts_h3', label: 'xP GW+3' },
    { key: 'price', label: 'Price' },
  ];

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        background: 'rgba(0,0,0,0.4)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          width: 520,
          maxHeight: '80vh',
          borderRadius: 12,
          background: theme.bg0,
          border: `1px solid ${theme.border}`,
          boxShadow: '0 20px 60px rgba(0,0,0,0.35)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div style={{
          padding: '14px 16px 10px',
          borderBottom: `1px solid ${theme.border}`,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          flexShrink: 0,
        }}>
          {filterPosition && (
            <div style={{
              padding: '2px 8px',
              borderRadius: 4,
              background: POSITION_COLORS[filterPosition] ?? theme.bg2,
              color: '#fff',
              fontSize: 10,
              fontWeight: 700,
              letterSpacing: '0.06em',
            }}>
              {filterPosition}
            </div>
          )}
          <input
            autoFocus
            placeholder="Search player, club..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              flex: 1,
              border: `1px solid ${theme.inputBorder}`,
              background: theme.inputBg,
              borderRadius: 6,
              padding: '6px 10px',
              fontSize: 13,
              color: theme.text1,
              outline: 'none',
              fontFamily: 'var(--font-dm-sans), system-ui, sans-serif',
            }}
          />
          <button
            onClick={onClose}
            style={{
              width: 28, height: 28,
              borderRadius: '50%',
              background: theme.bg2,
              border: 'none',
              cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 14, color: theme.text2, fontWeight: 700,
            }}
          >✕</button>
        </div>

        {/* Sort controls */}
        <div style={{
          padding: '8px 16px',
          borderBottom: `1px solid ${theme.border2}`,
          display: 'flex',
          gap: 6,
          flexShrink: 0,
        }}>
          {sortOptions.map(opt => (
            <button
              key={opt.key}
              onClick={() => setSortKey(opt.key)}
              style={{
                padding: '4px 10px',
                borderRadius: 5,
                border: `1px solid ${sortKey === opt.key ? theme.accentBorder : theme.border}`,
                background: sortKey === opt.key ? theme.accentBg : 'transparent',
                color: sortKey === opt.key ? theme.accent : theme.text2,
                fontSize: 11,
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              {opt.label}
            </button>
          ))}
          <div style={{ marginLeft: 'auto', fontSize: 11, color: theme.text3, alignSelf: 'center' }}>
            {filtered.length} players
          </div>
        </div>

        {/* Player list */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {filtered.map(player => {
            const firstFixture = player.fixtures?.[0];
            const xpVal = player[sortKey] != null ? Number(player[sortKey]) : null;
            const statusDot = player.status === 'd';
            const atCap = (clubCounts[player.club_short] ?? 0) >= 3;

            return (
              <div
                key={player.opta_code}
                onClick={atCap ? undefined : () => { onSelect(player); onClose(); }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '8px 16px',
                  borderBottom: `1px solid ${theme.border2}`,
                  cursor: atCap ? 'not-allowed' : 'pointer',
                  opacity: atCap ? 0.4 : 1,
                  transition: 'background 0.1s',
                }}
                onMouseEnter={e => { if (!atCap) e.currentTarget.style.background = theme.bg1; }}
                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
              >
                {/* Position badge */}
                <div style={{
                  width: 30,
                  flexShrink: 0,
                  display: 'flex',
                  justifyContent: 'center',
                }}>
                  <div style={{
                    padding: '2px 4px',
                    borderRadius: 3,
                    background: POSITION_COLORS[player.position] ?? theme.bg2,
                    color: '#fff',
                    fontSize: 8,
                    fontWeight: 700,
                    letterSpacing: '0.04em',
                  }}>
                    {player.position}
                  </div>
                </div>

                {/* Name + club */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span style={{
                      fontSize: 13,
                      fontWeight: 600,
                      color: theme.text1,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}>
                      {player.name}
                    </span>
                    {statusDot && (
                      <div style={{
                        width: 6, height: 6, borderRadius: '50%',
                        background: '#d97706', flexShrink: 0,
                      }}/>
                    )}
                  </div>
                  <div style={{ fontSize: 10, color: theme.text2 }}>{player.club}</div>
                </div>

                {/* Fixture */}
                {firstFixture && (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    flexShrink: 0,
                    minWidth: 70,
                  }}>
                    <div style={{
                      width: 7, height: 7, borderRadius: '50%',
                      background: firstFixture.difficulty != null
                        ? (DIFF_COLORS[firstFixture.difficulty] ?? '#9ca3af')
                        : '#9ca3af',
                      flexShrink: 0,
                    }}/>
                    <span style={{ fontSize: 11, color: theme.text2 }}>
                      {firstFixture.opponent}{firstFixture.is_home != null ? (firstFixture.is_home ? ' H' : ' A') : ''}
                    </span>
                  </div>
                )}

                {/* xP */}
                <div style={{
                  minWidth: 36,
                  textAlign: 'right',
                  fontSize: 13,
                  fontWeight: 700,
                  color: xpVal != null && xpVal >= 7 ? theme.success : theme.text1,
                  fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
                }}>
                  {xpVal != null ? xpVal.toFixed(1) : '—'}
                </div>

                {/* Price */}
                <div style={{
                  minWidth: 38,
                  textAlign: 'right',
                  fontSize: 12,
                  color: theme.text2,
                  fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
                }}>
                  £{player.price.toFixed(1)}
                </div>
              </div>
            );
          })}

          {filtered.length === 0 && (
            <div style={{
              padding: 32,
              textAlign: 'center',
              color: theme.text3,
              fontSize: 13,
            }}>
              No players found
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
