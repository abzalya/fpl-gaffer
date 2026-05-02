'use client';
import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { GameweekResponse } from '@/lib/api';
import { useCountdown } from '@/hooks/useCountdown';

interface HeaderProps {
  gameweek: GameweekResponse | null;
  isMock?: boolean;
  onAbout?: () => void;
}

export function Header({ gameweek, isMock, onAbout }: HeaderProps) {
  const theme = useTheme();
  const countdown = useCountdown(gameweek?.deadline ?? '');

  return (
    <header style={{
      flexShrink: 0,
      height: 48,
      display: 'flex',
      alignItems: 'center',
      padding: '0 20px',
      background: theme.bg0,
      borderBottom: `1px solid ${theme.border}`,
      gap: 0,
      zIndex: 10,
    }}>
      {/* Logo */}
      <div style={{
        fontSize: 15,
        fontWeight: 800,
        letterSpacing: '-0.03em',
        color: theme.text1,
        fontFamily: 'var(--font-dm-sans), system-ui, sans-serif',
      }}>
        fpl-<span style={{ color: theme.accent }}>gaffer</span>
      </div>

      {/* Vertical divider */}
      <div style={{ width: 1, height: 16, background: theme.border, margin: '0 14px' }}/>

      {/* GW name */}
      {gameweek && (
        <span style={{
          fontSize: 11,
          fontWeight: 600,
          color: theme.text2,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
        }}>
          {gameweek.name}
        </span>
      )}

      {/* Deadline + countdown */}
      {gameweek?.deadline && countdown && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          marginLeft: 12,
          padding: '3px 10px',
          borderRadius: 99,
          background: theme.accentBg,
          border: `1px solid ${theme.accentBorder}`,
        }}>
          <div style={{
            width: 6, height: 6, borderRadius: '50%',
            background: theme.accent,
            animation: 'pulse 2s ease-in-out infinite',
            flexShrink: 0,
          }}/>
          <span style={{
            fontSize: 10,
            fontWeight: 700,
            color: theme.text2,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
          }}>DEADLINE</span>
          <span style={{
            fontSize: 11,
            fontWeight: 700,
            color: theme.accent,
            fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
            fontVariantNumeric: 'tabular-nums',
          }}>
            {countdown}
          </span>
        </div>
      )}

      <div style={{ flex: 1 }}/>

      {/* About */}
      <button
        onClick={onAbout}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          fontSize: 11, fontWeight: 600, color: theme.text3,
          letterSpacing: '0.05em', padding: '4px 8px', borderRadius: 5,
          fontFamily: 'var(--font-dm-sans), system-ui, sans-serif',
          transition: 'color 0.15s',
          marginRight: isMock ? 10 : 0,
        }}
        onMouseEnter={e => (e.currentTarget.style.color = theme.text1)}
        onMouseLeave={e => (e.currentTarget.style.color = theme.text3)}
      >
        about
      </button>

      {/* Mock indicator */}
      {isMock && (
        <div style={{
          padding: '2px 8px',
          borderRadius: 4,
          background: theme.dangerBg,
          border: `1px solid ${theme.danger}44`,
          fontSize: 10,
          fontWeight: 700,
          color: theme.danger,
          letterSpacing: '0.06em',
        }}>
          MOCK
        </div>
      )}
    </header>
  );
}
