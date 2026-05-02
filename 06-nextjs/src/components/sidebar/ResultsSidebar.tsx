'use client';
import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { OptimizeResponse, PlayerResponse, GameweekResponse } from '@/lib/api';
import { enrichSquad } from '@/lib/enrichment';

interface ResultsSidebarProps {
  result: OptimizeResponse;
  allPlayers: PlayerResponse[];
  gameweek: GameweekResponse | null;
  onBack: () => void;
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
      marginBottom: 8,
      fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
    }}>
      {children}
    </div>
  );
}

function Divider() {
  const theme = useTheme();
  return <div style={{ height: 1, background: theme.border, margin: '2px 0' }}/>;
}

export function ResultsSidebar({ result, allPlayers, gameweek, onBack }: ResultsSidebarProps) {
  const theme = useTheme();
  const enriched = enrichSquad(result.squad.squad, allPlayers);
  const starters = enriched.filter(p => p.is_starter !== false);
  const horizon = result.horizon;

  // xP per GW - sum starters, double captain
  const xpPerGw: number[] = [];
  for (let i = 0; i < horizon; i++) {
    let sum = 0;
    for (const p of starters) {
      const ep = p.expected_pts?.[i];
      if (ep) {
        sum += p.is_captain ? ep.pts * 2 : ep.pts;
      }
    }
    xpPerGw.push(sum);
  }
  const totalXp = xpPerGw.reduce((a, b) => a + b, 0);

  // Captain per GW
  const captain = starters.find(p => p.is_captain);

  // Transfers
  const transfersIn = result.transfers_in?.transfers ?? [];
  const transfersOut = result.transfers_out?.transfers ?? [];
  const hasTransfers = transfersIn.length > 0;

  // Cost analysis
  const soldTotal = transfersOut.reduce((s, t) => s + t.price, 0);
  const boughtTotal = transfersIn.reduce((s, t) => s + t.price, 0);
  const netSpend = boughtTotal - soldTotal;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflowY: 'auto',
      padding: '14px 14px',
      gap: 14,
      fontFamily: 'var(--font-dm-sans), system-ui, sans-serif',
    }}>
      {/* Back + header */}
      <div>
        <button
          onClick={onBack}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            padding: '6px 10px',
            borderRadius: 6,
            border: `1px solid ${theme.border}`,
            background: theme.bg2,
            color: theme.text2,
            fontSize: 12,
            fontWeight: 600,
            cursor: 'pointer',
            marginBottom: 10,
            transition: 'all 0.15s',
          }}
          onMouseEnter={e => { e.currentTarget.style.color = theme.text1; }}
          onMouseLeave={e => { e.currentTarget.style.color = theme.text2; }}
        >
          ← Back to Setup
        </button>

        <div style={{ fontSize: 14, fontWeight: 700, color: theme.text1 }}>Optimal Squad</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
          {gameweek && (
            <span style={{ fontSize: 11, color: theme.text2 }}>{gameweek.name}</span>
          )}
          <div style={{
            padding: '1px 6px', borderRadius: 3,
            background: result.status === 'optimal' ? theme.accentBg : theme.bg2,
            border: `1px solid ${result.status === 'optimal' ? theme.accentBorder : theme.border}`,
            fontSize: 9, fontWeight: 700,
            color: result.status === 'optimal' ? theme.accent : theme.text2,
            letterSpacing: '0.05em',
          }}>
            {result.status?.toUpperCase()}
          </div>
          <span style={{
            fontSize: 9,
            color: theme.text3,
            fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
          }}>
            {result.solve_time_ms}ms
          </span>
        </div>
      </div>

      <Divider/>

      {/* Expected Points */}
      <div>
        <SectionLabel>Expected Points</SectionLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
          {xpPerGw.map((xp, i) => {
            const gwNum = enriched[0]?.expected_pts?.[i]?.gw ?? (i + 1);
            return (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '7px 10px',
                borderRadius: 6,
                background: theme.bg1,
                border: `1px solid ${theme.border2}`,
              }}>
                <span style={{ fontSize: 11, color: theme.text2 }}>GW{gwNum}</span>
                <span style={{
                  fontSize: 15,
                  fontWeight: 700,
                  color: theme.text1,
                  fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
                }}>
                  {xp.toFixed(1)}
                </span>
              </div>
            );
          })}
          {horizon > 1 && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '7px 10px',
              borderRadius: 6,
              background: theme.accentBg,
              border: `1px solid ${theme.accentBorder}`,
            }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: theme.accent }}>TOTAL</span>
              <span style={{
                fontSize: 15,
                fontWeight: 700,
                color: theme.accent,
                fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
              }}>
                {totalXp.toFixed(1)}
              </span>
            </div>
          )}
        </div>
      </div>

      <Divider/>

      {/* Captain per GW */}
      {captain && (
        <div>
          <SectionLabel>Captain{horizon > 1 ? ' per GW' : ''}</SectionLabel>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
            {captain.expected_pts?.slice(0, horizon).map((ep, i) => {
              const fix = captain.fixtures?.find(f => f.horizon === i + 1);
              return (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '7px 10px',
                  borderRadius: 6,
                  background: theme.accent2Bg,
                  border: `1px solid ${theme.accent2Border}`,
                }}>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: theme.text1 }}>
                      {captain.name}
                    </div>
                    {fix && (
                      <div style={{ fontSize: 9, color: theme.text3 }}>
                        vs {fix.opponent}{fix.is_home != null ? (fix.is_home ? ' (H)' : ' (A)') : ''}
                      </div>
                    )}
                  </div>
                  <span style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: theme.accent2,
                    fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
                  }}>
                    {(ep.pts * 2).toFixed(1)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Transfers */}
      {hasTransfers && (
        <>
          <Divider/>
          <div>
            <SectionLabel>Transfers</SectionLabel>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              {transfersOut.map((tout, i) => {
                const tin = transfersIn[i];
                return (
                  <div key={i} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '6px 8px',
                    borderRadius: 6,
                    background: theme.bg1,
                    border: `1px solid ${theme.border2}`,
                  }}>
                    <div style={{
                      flex: 1,
                      padding: '4px 7px',
                      borderRadius: 5,
                      background: theme.dangerBg,
                      border: `1px solid ${theme.danger}33`,
                    }}>
                      <div style={{ fontSize: 10, fontWeight: 600, color: theme.danger }}>OUT</div>
                      <div style={{ fontSize: 11, fontWeight: 600, color: theme.text1, marginTop: 1 }}>{tout.name}</div>
                      <div style={{ fontSize: 9, color: theme.text3 }}>£{tout.price.toFixed(1)}</div>
                    </div>
                    <span style={{ fontSize: 14, color: theme.text3 }}>→</span>
                    {tin && (
                      <div style={{
                        flex: 1,
                        padding: '4px 7px',
                        borderRadius: 5,
                        background: 'rgba(34,197,94,0.08)',
                        border: '1px solid rgba(34,197,94,0.25)',
                      }}>
                        <div style={{ fontSize: 10, fontWeight: 600, color: theme.success }}>IN</div>
                        <div style={{ fontSize: 11, fontWeight: 600, color: theme.text1, marginTop: 1 }}>{tin.name}</div>
                        <div style={{ fontSize: 9, color: theme.text3 }}>£{tin.price.toFixed(1)}</div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <Divider/>

          {/* Cost Analysis */}
          <div>
            <SectionLabel>Cost Analysis</SectionLabel>
            <div style={{
              padding: '8px 10px',
              borderRadius: 6,
              background: theme.bg1,
              border: `1px solid ${theme.border2}`,
              display: 'flex',
              flexDirection: 'column',
              gap: 5,
            }}>
              {[
                { label: 'Sold', value: soldTotal, color: theme.danger },
                { label: 'Bought', value: boughtTotal, color: theme.success },
                { label: 'Net', value: netSpend, color: netSpend <= 0 ? theme.success : theme.danger },
              ].map(row => (
                <div key={row.label} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}>
                  <span style={{ fontSize: 11, color: theme.text2 }}>{row.label}</span>
                  <span style={{
                    fontSize: 12,
                    fontWeight: 700,
                    color: row.color,
                    fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
                  }}>
                    {netSpend <= 0 && row.label === 'Net' ? '' : ''}£{Math.abs(row.value).toFixed(1)}
                    {row.label === 'Net' ? (netSpend > 0 ? ' spent' : ' saved') : ''}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Footer */}
      <div style={{ flex: 1, minHeight: 8 }}/>
      <div style={{
        fontSize: 9,
        color: theme.text3,
        textAlign: 'center',
        fontFamily: 'var(--font-dm-mono), DM Mono, monospace',
      }}>
        PuLP CBC · {result.solve_time_ms}ms
      </div>
    </div>
  );
}
