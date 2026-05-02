import React from 'react';

export type KitDef = {
  p: string;
  s: string;
  gkp: string;
  render: (p: string, s: string) => React.ReactNode;
};

export const KIT_PATTERNS: Record<string, KitDef> = {
  ARS: { p:'#EF0107', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M9 13 L9 23 L3 11Z" fill={s} opacity="0.9"/>
      <path d="M41 13 L41 23 L47 11Z" fill={s} opacity="0.9"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
      <rect x="20" y="5" width="10" height="4" rx="1" fill={s} opacity="0.6"/>
    </>
  },
  AVL: { p:'#670E36', s:'#95BFE5', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M9 13 L9 23 L3 11Z" fill={s}/>
      <path d="M41 13 L41 23 L47 11Z" fill={s}/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
    </>
  },
  BOU: { p:'#DA291C', s:'#000000', gkp:'#00A86B',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <rect x="16" y="5" width="4" height="43" fill={s} opacity="0.85"/>
      <rect x="23" y="9" width="4" height="39" fill={s} opacity="0.85"/>
      <rect x="30" y="5" width="4" height="43" fill={s} opacity="0.85"/>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill="none" stroke={s} strokeWidth="0.8"/>
    </>
  },
  BRE: { p:'#E30613', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <rect x="19" y="5" width="4" height="43" fill={s} opacity="0.9"/>
      <rect x="27" y="5" width="4" height="43" fill={s} opacity="0.9"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.2"/>
    </>
  },
  BRI: { p:'#0057B8', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <rect x="18" y="5" width="5" height="43" fill={s} opacity="0.9"/>
      <rect x="27" y="5" width="5" height="43" fill={s} opacity="0.9"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.2"/>
    </>
  },
  CHE: { p:'#034694', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
      <line x1="9" y1="23" x2="41" y2="23" stroke={s} strokeWidth="1" opacity="0.3"/>
    </>
  },
  CRY: { p:'#1B458F', s:'#C4122E', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M17 5 L33 5 L41 48 L25 48Z" fill={s} opacity="0.85"/>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="0.6"/>
    </>
  },
  EVE: { p:'#003399', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
    </>
  },
  FUL: { p:'#FFFFFF', s:'#000000', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p} stroke={s} strokeWidth="1"/>
      <path d="M9 13 L9 23 L3 11Z" fill={s} opacity="0.8"/>
      <path d="M41 13 L41 23 L47 11Z" fill={s} opacity="0.8"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
    </>
  },
  IPS: { p:'#0044A9', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
      <line x1="9" y1="23" x2="41" y2="23" stroke={s} strokeWidth="1" opacity="0.25"/>
    </>
  },
  LEI: { p:'#003090', s:'#FDBE11', gkp:'#FF6B6B',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <line x1="9" y1="23" x2="41" y2="23" stroke={s} strokeWidth="2.5"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
    </>
  },
  LIV: { p:'#C8102E', s:'#FFFFFF', gkp:'#00A86B',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M17 5 L9 13 L9 23 L20 23 L20 5 Q18.5 7 17 5Z" fill={s} opacity="0.25"/>
      <path d="M33 5 L41 13 L41 23 L30 23 L30 5 Q31.5 7 33 5Z" fill={s} opacity="0.25"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
    </>
  },
  MCI: { p:'#6CABDD', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <line x1="20" y1="5" x2="20" y2="48" stroke={s} strokeWidth="0.8" opacity="0.5"/>
      <line x1="25" y1="9" x2="25" y2="48" stroke={s} strokeWidth="0.8" opacity="0.5"/>
      <line x1="30" y1="5" x2="30" y2="48" stroke={s} strokeWidth="0.8" opacity="0.5"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
    </>
  },
  MUN: { p:'#DA291C', s:'#000000', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M9 13 L9 23 L3 11Z" fill={s} opacity="0.7"/>
      <path d="M41 13 L41 23 L47 11Z" fill={s} opacity="0.7"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
      <rect x="22" y="5" width="6" height="5" rx="1" fill={s} opacity="0.5"/>
    </>
  },
  NEW: { p:'#241F20', s:'#FFFFFF', gkp:'#FF6B6B',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L25 48 L25 5 Q21 10 17 5Z" fill={s}/>
      <path d="M25 5 L25 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10Z" fill={p}/>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill="none" stroke="rgba(0,0,0,0.2)" strokeWidth="0.6"/>
    </>
  },
  NFO: { p:'#DD0000', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
      <line x1="9" y1="25" x2="41" y2="25" stroke={s} strokeWidth="1.2" opacity="0.3"/>
    </>
  },
  SOU: { p:'#D71920', s:'#FFFFFF', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L25 48 L25 5 Q21 10 17 5Z" fill={p}/>
      <path d="M25 5 L25 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10Z" fill={s}/>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill="none" stroke={s} strokeWidth="0.5"/>
    </>
  },
  TOT: { p:'#FFFFFF', s:'#132257', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p} stroke={s} strokeWidth="0.8"/>
      <path d="M9 13 L9 23 L3 11Z" fill={s}/>
      <path d="M41 13 L41 23 L47 11Z" fill={s}/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="2"/>
      <rect x="22" y="5" width="6" height="4" rx="1" fill={s}/>
    </>
  },
  WHU: { p:'#7A263A', s:'#1BB1E7', gkp:'#FFD700',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M9 13 L9 23 L3 11Z" fill={s}/>
      <path d="M41 13 L41 23 L47 11Z" fill={s}/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
    </>
  },
  WOL: { p:'#FDB913', s:'#231F20', gkp:'#6CABDD',
    render: (p,s) => <>
      <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
      <path d="M9 13 L9 23 L3 11Z" fill={s} opacity="0.6"/>
      <path d="M41 13 L41 23 L47 11Z" fill={s} opacity="0.6"/>
      <line x1="9" y1="23" x2="41" y2="23" stroke={s} strokeWidth="2"/>
      <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
    </>
  },
};

export const FALLBACK_KIT: KitDef = {
  p:'#4B5563', s:'#9CA3AF', gkp:'#FFD700',
  render: (p,s) => <>
    <path d="M17 5 L9 13 L3 11 L1 21 L9 23 L9 48 L41 48 L41 23 L49 21 L47 11 L41 13 L33 5 Q29 10 25 10 Q21 10 17 5Z" fill={p}/>
    <path d="M17 5 Q21 10 25 10 Q29 10 33 5" fill="none" stroke={s} strokeWidth="1.5"/>
  </>
};
