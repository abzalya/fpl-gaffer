'use client';
import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { GameweekResponse } from '@/lib/api';
import { useCountdown } from '@/hooks/useCountdown';

interface SetupSidebarProps {
  gameweek: GameweekResponse | null;
  horizon: 1 | 2 | 3;
  bank: number;
  freeTransfers: number;
  chip: string | null;
  squadCount: number;
  squadValue: number;
  loading: boolean;
  error: string | null;
  onHorizon: (v: 1 | 2 | 3) => void;
  onBank: (v: number) => void;
  onFreeTransfers: (v: number) => void;
  onChip: (v: string | null) => void;
  onOptimise: () => void;
}

function Divider() {
  const theme = useTheme();
  return <div style={{ height: 1, background: theme.border, margin: '2px 0' }}/>;
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  const theme = useTheme();
  return (
    <div style={{
      fontSize: 9,
      fontWeight: 700,
      letterSpacing: '0.1em',
      color: theme.text3,
      textTransform: 'uppercase',
      marginBottom: 6,
      fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
    }}>
      {children}
    </div>
  );
}

const CHIPS = [
  { key: 'wildcard', label: 'Wildcard' },
  { key: 'free_hit', label: 'Free Hit' },
  { key: 'bench_boost', label: 'Bench Boost' },
  { key: 'triple_captain', label: 'Triple Cap' },
];

function gwRangeLabel(h: number, gwId?: number): string {
  if (!gwId) return '';
  if (h === 1) return `GW${gwId}`;
  return `GW${gwId}–${gwId + h - 1}`;
}

export function SetupSidebar({
  gameweek,
  horizon,
  bank,
  freeTransfers,
  chip,
  squadCount,
  squadValue,
  loading,
  error,
  onHorizon,
  onBank,
  onFreeTransfers,
  onChip,
  onOptimise,
}: SetupSidebarProps) {
  const theme = useTheme();
  const countdown = useCountdown(gameweek?.deadline ?? '');

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflowY: 'auto',
      padding: '16px 14px',
      gap: 14,
      fontFamily: 'var(--font-dm-sans), system-ui, sans-serif',
    }}>
      {/* Section 1: Optimising For */}
      <div>
        <SectionLabel>Optimising For</SectionLabel>
        <div style={{
          padding: '10px 12px',
          borderRadius: 8,
          background: theme.bg1,
          border: `1px solid ${theme.border}`,
        }}>
          <div style={{ fontSize: 17, fontWeight: 700, color: theme.text1 }}>
            {gameweek?.name ?? '—'}
          </div>
          {gameweek?.deadline && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
              <div style={{
                width: 6, height: 6, borderRadius: '50%',
                background: theme.accent,
                animation: 'pulse 2s ease-in-out infinite',
                flexShrink: 0,
              }}/>
              <span style={{ fontSize: 10, color: theme.text2, fontWeight: 500 }}>Deadline</span>
              <span style={{
                fontSize: 11,
                fontWeight: 700,
                color: theme.accent,
                fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
              }}>
                {countdown}
              </span>
            </div>
          )}
        </div>
      </div>

      <Divider/>

      {/* Section 2: Planning Horizon */}
      <div>
        <SectionLabel>Planning Horizon</SectionLabel>
        <div style={{ display: 'flex', gap: 6 }}>
          {([1, 2, 3] as const).map(h => (
            <button
              key={h}
              onClick={() => onHorizon(h)}
              style={{
                flex: 1,
                padding: '7px 4px',
                borderRadius: 6,
                border: `1px solid ${horizon === h ? theme.accentBorder : theme.border}`,
                background: horizon === h ? theme.accentBg : 'transparent',
                color: horizon === h ? theme.accent : theme.text2,
                fontSize: 12,
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.15s',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
              }}
            >
              <span>{h}GW</span>
              <span style={{ fontSize: 9, fontWeight: 500, opacity: 0.7 }}>{gwRangeLabel(h, gameweek?.gameweek_id)}</span>
            </button>
          ))}
        </div>
      </div>

      <Divider/>

      {/* Section 3: Budget */}
      <div>
        <SectionLabel>Budget</SectionLabel>
        <div style={{ display: 'flex', gap: 6, marginBottom: 6 }}>
          <div style={{
            flex: 1,
            padding: '8px 10px',
            borderRadius: 6,
            background: theme.bg1,
            border: `1px solid ${theme.border}`,
          }}>
            <div style={{ fontSize: 8, color: theme.text3, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 3 }}>Squad Value</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: theme.text1, fontFamily: 'var(--font-dm-mono), DM Mono, monospace' }}>
              £{squadValue.toFixed(1)}
            </div>
          </div>
          <div style={{
            flex: 1,
            padding: '8px 10px',
            borderRadius: 6,
            background: theme.bg1,
            border: `1px solid ${theme.border}`,
          }}>
            <div style={{ fontSize: 8, color: theme.text3, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 3 }}>In The Bank</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: theme.accent, fontFamily: 'var(--font-dm-mono), DM Mono, monospace' }}>
              £{bank.toFixed(1)}
            </div>
          </div>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '7px 10px',
          borderRadius: 6,
          border: `1px solid ${theme.inputBorder}`,
          background: theme.inputBg,
        }}>
          <span style={{ fontSize: 11, color: theme.text3, fontWeight: 600 }}>ITB £</span>
          <input
            type="number"
            step={0.1}
            min={0}
            max={20}
            value={bank}
            onChange={e => onBank(parseFloat(e.target.value) || 0)}
            style={{
              flex: 1,
              border: 'none',
              background: 'transparent',
              color: theme.text1,
              fontSize: 14,
              fontWeight: 600,
              fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
              outline: 'none',
            }}
          />
        </div>
      </div>

      {/* Section 4: Free Transfers */}
      <div>
        <SectionLabel>Free Transfers</SectionLabel>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            onClick={() => onFreeTransfers(Math.max(0, freeTransfers - 1))}
            style={{
              width: 30, height: 30, borderRadius: 6,
              border: `1px solid ${theme.border}`,
              background: theme.bg2,
              color: theme.text1,
              fontSize: 18, fontWeight: 700,
              cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >−</button>
          <div style={{
            flex: 1, textAlign: 'center',
            fontSize: 18, fontWeight: 700,
            color: theme.text1,
            fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
          }}>
            {freeTransfers}
          </div>
          <button
            onClick={() => onFreeTransfers(Math.min(5, freeTransfers + 1))}
            style={{
              width: 30, height: 30, borderRadius: 6,
              border: `1px solid ${theme.border}`,
              background: theme.bg2,
              color: theme.text1,
              fontSize: 18, fontWeight: 700,
              cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >+</button>
        </div>
        {freeTransfers === 0 && (
          <div style={{
            marginTop: 5,
            fontSize: 10,
            color: theme.danger,
            fontWeight: 600,
            padding: '3px 6px',
            borderRadius: 4,
            background: theme.dangerBg,
          }}>
            −4 pts per additional transfer
          </div>
        )}
      </div>

      <Divider/>

      {/* Section 5: Chip */}
      <div>
        <SectionLabel>Chip</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
          {CHIPS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => onChip(chip === key ? null : key)}
              style={{
                padding: '7px 12px',
                borderRadius: 6,
                border: `1px solid ${chip === key ? theme.accentBorder : theme.border}`,
                background: chip === key ? theme.accentBg : 'transparent',
                color: chip === key ? theme.accent : theme.text2,
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s',
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <Divider/>

      {/* Section 6: Squad count */}
      <div>
        <SectionLabel>Squad</SectionLabel>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontSize: 11, color: theme.text2 }}>Players selected</span>
          <span style={{
            fontSize: 13,
            fontWeight: 700,
            color: squadCount === 15 ? theme.accent : theme.text1,
            fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
          }}>
            {squadCount}/15
          </span>
        </div>
        {/* Progress bar */}
        <div style={{
          height: 5,
          borderRadius: 3,
          background: theme.bg3,
          overflow: 'hidden',
        }}>
          <div style={{
            height: '100%',
            width: `${(squadCount / 15) * 100}%`,
            borderRadius: 3,
            background: squadCount === 15 ? theme.accent : theme.text3,
            transition: 'width 0.3s ease',
          }}/>
        </div>
      </div>

      <div style={{ flex: 1, minHeight: 8 }}/>

      {/* Error */}
      {error && (
        <div style={{
          padding: '8px 10px',
          borderRadius: 6,
          background: theme.dangerBg,
          border: `1px solid ${theme.danger}44`,
          fontSize: 11,
          color: theme.danger,
          fontWeight: 500,
        }}>
          {error}
        </div>
      )}

      {/* Optimise button */}
      <button
        onClick={onOptimise}
        disabled={loading}
        style={{
          width: '100%',
          padding: '11px 16px',
          borderRadius: 8,
          border: 'none',
          background: loading ? theme.bg3 : theme.accent,
          color: loading ? theme.text3 : theme.btnText,
          fontSize: 13,
          fontWeight: 700,
          cursor: loading ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8,
          transition: 'background 0.2s',
          letterSpacing: '0.02em',
        }}
      >
        {loading && (
          <div style={{
            width: 14, height: 14,
            border: `2px solid ${theme.btnText}44`,
            borderTopColor: theme.btnText,
            borderRadius: '50%',
            animation: 'spin 0.7s linear infinite',
          }}/>
        )}
        {loading ? 'Optimising…' : 'Optimise Squad'}
      </button>
      {squadCount === 0 && (
        <div style={{
          textAlign: 'center',
          fontSize: 10,
          color: theme.text3,
          fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
          letterSpacing: '0.04em',
        }}>
          building new team
        </div>
      )}
    </div>
  );
}
