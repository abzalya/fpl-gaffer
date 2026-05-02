'use client';
import React, { createContext, useContext, useMemo } from 'react';
import { buildTheme, THEME_DEFAULTS, Theme } from '@/lib/theme';

const ThemeContext = createContext<Theme | null>(null);

export function ThemeProvider({ children, bgBase, accentGreen, accentPurple }: {
  children: React.ReactNode;
  bgBase?: string;
  accentGreen?: string;
  accentPurple?: string;
}) {
  const theme = useMemo(
    () => buildTheme(bgBase ?? THEME_DEFAULTS.bgBase, accentGreen ?? THEME_DEFAULTS.accentGreen, accentPurple ?? THEME_DEFAULTS.accentPurple),
    [bgBase, accentGreen, accentPurple]
  );
  return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>;
}

export function useTheme(): Theme {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
