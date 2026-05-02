'use client';
import { useState, useEffect } from 'react';
import {
  getPlayers, getNextGameweek,
  PlayerResponse, GameweekResponse, OptimizeRequest,
} from '@/lib/api';
import { useOptimise } from '@/hooks/useOptimise';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Header } from '@/components/Header';
import { Pitch } from '@/components/pitch/Pitch';
import { SetupSidebar } from '@/components/sidebar/SetupSidebar';
import { ResultsSidebar } from '@/components/sidebar/ResultsSidebar';
import { PlayerPicker } from '@/components/PlayerPicker';
import { AboutModal } from '@/components/AboutModal';

export type PlayerWithLocked = PlayerResponse & { locked: boolean };

function AppShell() {
  const theme = useTheme();

  const [phase, setPhase] = useState<'setup' | 'results'>('setup');
  const [gameweek, setGameweek] = useState<GameweekResponse | null>(null);
  const [allPlayers, setAllPlayers] = useState<PlayerResponse[]>([]);
  const [squad, setSquad] = useState<PlayerWithLocked[]>([]);
  const [horizon, setHorizon] = useState<1 | 2 | 3>(2);
  const [bank, setBank] = useState(0.5);
  const [freeTransfers, setFreeTransfers] = useState(1);
  const [chip, setChip] = useState<string | null>(null);
  const [pickerOpen, setPickerOpen] = useState(false);
  const [pickerPosition, setPickerPosition] = useState<string | null>(null);
  const [aboutOpen, setAboutOpen] = useState(false);

  const { loading, error, result, run, reset } = useOptimise(allPlayers);

  useEffect(() => {
    getPlayers().then(setAllPlayers).catch(console.error);
    getNextGameweek().then(setGameweek).catch(console.error);
  }, []);

  function handleSlotClick(pos: string) {
    setPickerPosition(pos);
    setPickerOpen(true);
  }

  function handleSelectPlayer(player: PlayerResponse) {
    setSquad(prev => {
      if (prev.some(p => p.opta_code === player.opta_code)) return prev;
      return [...prev, { ...player, locked: false }];
    });
  }

  function handleRemovePlayer(player: PlayerWithLocked) {
    setSquad(prev => prev.filter(p => p.opta_code !== player.opta_code));
  }

  function handleLockPlayer(player: PlayerWithLocked) {
    setSquad(prev => prev.map(p =>
      p.opta_code === player.opta_code ? { ...p, locked: !p.locked } : p
    ));
  }

  async function handleOptimize() {
    const req: OptimizeRequest = {
      existing_squad: squad.map(p => ({ opta_code: p.opta_code, locked: p.locked })),
      chips: {
        wildcard: chip === 'wildcard',
        free_hit: chip === 'free_hit',
        bench_boost: chip === 'bench_boost',
        triple_captain: chip === 'triple_captain',
      },
      bank,
      free_transfers: freeTransfers,
      horizon,
    };
    const ok = await run(req);
    if (ok) setPhase('results');
  }

  function handleBack() {
    reset();
    setPhase('setup');
  }

  const displaySquad = phase === 'results' && result
    ? result.squad
    : squad;

  const transfersIn = result?.transfersIn ?? [];
  const transfersOut = result?.transfersOut ?? [];

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: theme.bg0,
      overflow: 'hidden',
      fontFamily: 'var(--font-dm-sans), system-ui, sans-serif',
    }}>
      <Header gameweek={gameweek} onAbout={() => setAboutOpen(true)}/>

      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* 70% pitch area */}
        <div style={{
          flex: '0 0 70%',
          overflowY: 'auto',
          borderRight: `1px solid ${theme.border}`,
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'center',
          padding: '16px 12px 24px',
        }}>
          <div className="fade-in">
            <Pitch
              squad={displaySquad as Parameters<typeof Pitch>[0]['squad']}
              onSlotClick={phase === 'setup' ? handleSlotClick : undefined}
              onRemovePlayer={phase === 'setup' ? (p) => handleRemovePlayer(p as PlayerWithLocked) : undefined}
              onLockPlayer={phase === 'setup' ? (p) => handleLockPlayer(p as PlayerWithLocked) : undefined}
              resultsMode={phase === 'results'}
              transfersIn={transfersIn}
              transfersOut={transfersOut}
              horizon={horizon}
            />
          </div>
        </div>

        {/* 30% sidebar */}
        <div style={{
          flex: '0 0 30%',
          overflowY: 'auto',
          background: theme.sidebarBg,
        }}>
          {phase === 'setup' ? (
            <SetupSidebar
              gameweek={gameweek}
              horizon={horizon}
              bank={bank}
              freeTransfers={freeTransfers}
              chip={chip}
              squadCount={squad.length}
              loading={loading}
              error={error}
              onHorizon={setHorizon}
              onBank={setBank}
              onFreeTransfers={setFreeTransfers}
              onChip={setChip}
              onOptimise={handleOptimize}
            />
          ) : result ? (
            <ResultsSidebar
              result={result.raw}
              allPlayers={allPlayers}
              gameweek={gameweek}
              onBack={handleBack}
            />
          ) : null}
        </div>
      </div>

      {aboutOpen && <AboutModal onClose={() => setAboutOpen(false)}/>}

      {pickerOpen && (
        <PlayerPicker
          filterPosition={pickerPosition}
          currentSquad={squad}
          allPlayers={allPlayers}
          onSelect={handleSelectPlayer}
          onClose={() => setPickerOpen(false)}
        />
      )}
    </div>
  );
}

export default function Home() {
  return (
    <ThemeProvider bgBase="#f5f0e8" accentGreen="#c2410c" accentPurple="#92400e">
      <AppShell/>
    </ThemeProvider>
  );
}
