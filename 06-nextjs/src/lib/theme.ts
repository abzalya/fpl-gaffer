export type Theme = {
  isLight: boolean;
  accent: string;
  accent2: string;
  bg0: string;
  bg1: string;
  bg2: string;
  bg3: string;
  text1: string;
  text2: string;
  text3: string;
  border: string;
  border2: string;
  accentBg: string;
  accentBorder: string;
  accent2Bg: string;
  accent2Border: string;
  danger: string;
  dangerBg: string;
  success: string;
  btnText: string;
  inputBorder: string;
  inputBg: string;
  sidebarBg: string;
  shadow: string;
};

export const THEME_DEFAULTS = {
  bgBase: '#f5f0e8',
  accentGreen: '#c2410c',
  accentPurple: '#92400e',
};

export function buildTheme(bgBase: string, accentGreen?: string, accentPurple?: string): Theme {
  const bgHex = bgBase.replace('#', '');
  let isLight = false;
  if (bgHex.length === 6) {
    const r = parseInt(bgHex.slice(0, 2), 16), g = parseInt(bgHex.slice(2, 4), 16), b = parseInt(bgHex.slice(4, 6), 16);
    isLight = (r * 0.299 + g * 0.587 + b * 0.114) > 140;
  }
  const accent = accentGreen || (isLight ? '#c2410c' : '#22c55e');
  const accent2 = accentPurple || (isLight ? '#92400e' : '#8b5cf6');

  if (isLight) {
    return {
      isLight, accent, accent2,
      bg0: bgBase,
      bg1: 'rgba(0,0,0,0.04)',
      bg2: 'rgba(0,0,0,0.07)',
      bg3: 'rgba(0,0,0,0.11)',
      text1: '#1c1008',
      text2: '#6b4c2a',
      text3: '#a8917a',
      border: 'rgba(0,0,0,0.1)',
      border2: 'rgba(0,0,0,0.06)',
      accentBg: `${accent}18`,
      accentBorder: `${accent}55`,
      accent2Bg: `${accent2}18`,
      accent2Border: `${accent2}55`,
      danger: '#dc2626',
      dangerBg: 'rgba(220,38,38,0.08)',
      success: '#16a34a',
      btnText: '#fff',
      inputBorder: 'rgba(0,0,0,0.15)',
      inputBg: 'rgba(0,0,0,0.06)',
      sidebarBg: 'rgba(0,0,0,0.05)',
      shadow: '0 1px 3px rgba(0,0,0,0.12)',
    };
  } else {
    return {
      isLight, accent, accent2,
      bg0: bgBase,
      bg1: 'rgba(255,255,255,0.04)',
      bg2: 'rgba(255,255,255,0.07)',
      bg3: 'rgba(255,255,255,0.10)',
      text1: '#f1f5f9',
      text2: '#94a3b8',
      text3: '#4b5563',
      border: 'rgba(255,255,255,0.08)',
      border2: 'rgba(255,255,255,0.05)',
      accentBg: `${accent}22`,
      accentBorder: `${accent}55`,
      accent2Bg: `${accent2}22`,
      accent2Border: `${accent2}55`,
      danger: '#ef4444',
      dangerBg: 'rgba(239,68,68,0.12)',
      success: '#22c55e',
      btnText: '#fff',
      inputBorder: 'rgba(255,255,255,0.12)',
      inputBg: 'rgba(255,255,255,0.06)',
      sidebarBg: 'rgba(0,0,0,0.18)',
      shadow: '0 1px 3px rgba(0,0,0,0.4)',
    };
  }
}
