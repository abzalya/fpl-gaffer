'use client';
import React from 'react';

export function StatusOverlay({ status }: { status?: string }) {
  if (!status || status === 'a') return null;

  let bg = '#6b7280';
  let label = '–';

  if (status === 'd') {
    bg = '#d97706';
    label = '?';
  } else if (status === 'i') {
    bg = '#dc2626';
    label = '✕';
  } else if (status === 's') {
    bg = '#ea580c';
    label = 'S';
  } else if (status === 'u') {
    bg = '#6b7280';
    label = '–';
  }

  return (
    <div style={{
      position: 'absolute',
      bottom: -3,
      right: -3,
      width: 14,
      height: 14,
      borderRadius: '50%',
      background: bg,
      border: '1.5px solid rgba(255,255,255,0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: 7,
      fontWeight: 700,
      color: '#fff',
      zIndex: 5,
    }}>
      {label}
    </div>
  );
}
