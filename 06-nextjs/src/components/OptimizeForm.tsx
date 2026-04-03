//POST /optimize form
//pass players. return enriched squad. 
//Version: 1.0.0

"use client";

import React, {useState} from "react";
import {PlayerResponse, postOptimize} from "@/lib/api";
import {EnrichedPlayer, enrichSquad} from "@/lib/enrichment";
import PlayerSearchInput from "@/components/PlayerSearchInput";
import OptimizeResult from "@/components/OptimizeResult";

type Props = {
    players: PlayerResponse[];
};

export default function OptimizeForm({players}: Props) {
    const [horizon, setHorizon] = useState("3");
    const [bank, setBank] = useState("0");
    const [freeTransfers, setFreeTransfers] = useState("0");
    const [wildcard, setWildcard] = useState(false);
    const [freeHit, setFreeHit] = useState(false);
    const [benchBoost, setBenchBoost] = useState(false);
    const [tripleCaptain, setTripleCaptain] = useState(false);
    const [existingSquad, setExistingSquad] = useState<{ opta_code: number | null; locked: boolean }[]>(
        Array(15).fill(null).map(() => ({ opta_code: null, locked: false }))
    );
    const [optimizeResult, setOptimizeResult] = useState<null | object>(null);
    const [enrichedSquad, setEnrichedSquad] = useState<EnrichedPlayer[]>([]);

    const setPlayerInSquad = (index: number, opta_code: number) => {
        const updatedSquad = [...existingSquad];
        updatedSquad[index] = {...updatedSquad[index], opta_code};
        setExistingSquad(updatedSquad);
    }
 
    const setLockPlayerInSquad = (index: number,  e: React.ChangeEvent<HTMLInputElement>) => {
        const updatedSquad = [...existingSquad];
        updatedSquad[index] = {...updatedSquad[index], locked: e.target.checked};
        setExistingSquad(updatedSquad);
    }
    
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const response = await postOptimize({
            existing_squad: existingSquad.filter(p => p.opta_code !== null) as {opta_code: number; locked: boolean}[],
            chips: {wildcard: wildcard, free_hit: freeHit, bench_boost: benchBoost, triple_captain: tripleCaptain},
            bank: Number(bank),
            free_transfers: Number(freeTransfers),
            horizon: Number(horizon),
        });
        setOptimizeResult(response);
        setEnrichedSquad(enrichSquad(response.squad.squad, players));
    }

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <div> FORM Testing</div>
                <input type="number" value={horizon} onChange={(e) => setHorizon(e.target.value)} />
                <input type="number" value={bank} onChange={(e) => setBank(e.target.value)} />
                <input type="number" value={freeTransfers} onChange={(e) => setFreeTransfers(e.target.value)} />
                <div>
                    <input type="checkbox" checked={wildcard} onChange={(e) => setWildcard(e.target.checked)} /> Wildcard
                    <input type="checkbox" checked={freeHit} onChange={(e) => setFreeHit(e.target.checked)} /> Free Hit
                    <input type="checkbox" checked={benchBoost} onChange={(e) => setBenchBoost(e.target.checked)} /> Bench Boost
                    <input type="checkbox" checked={tripleCaptain} onChange={(e) => setTripleCaptain(e.target.checked)} /> Triple Captain
                </div>
                <div> existing squad
                    <div>
                        GKPs
                        <PlayerSearchInput players={players} preSetPosition="GKP" onChange={(opta_code) => setPlayerInSquad(0, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[0].locked} onChange={(e) => setLockPlayerInSquad(0, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="GKP" onChange={(opta_code) => setPlayerInSquad(1, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[1].locked} onChange={(e) => setLockPlayerInSquad(1, e)} /> Locked
                    </div>
                    <div>
                        DEFs
                        <PlayerSearchInput players={players} preSetPosition="DEF" onChange={(opta_code) => setPlayerInSquad(2, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[2].locked} onChange={(e) => setLockPlayerInSquad(2, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="DEF" onChange={(opta_code) => setPlayerInSquad(3, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[3].locked} onChange={(e) => setLockPlayerInSquad(3, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="DEF" onChange={(opta_code) => setPlayerInSquad(4, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[4].locked} onChange={(e) => setLockPlayerInSquad(4, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="DEF" onChange={(opta_code) => setPlayerInSquad(5, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[5].locked} onChange={(e) => setLockPlayerInSquad(5, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="DEF" onChange={(opta_code) => setPlayerInSquad(6, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[6].locked} onChange={(e) => setLockPlayerInSquad(6, e)} /> Locked
                    </div>
                    <div>
                        MIDs
                        <PlayerSearchInput players={players} preSetPosition="MID" onChange={(opta_code) => setPlayerInSquad(7, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[7].locked} onChange={(e) => setLockPlayerInSquad(7, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="MID" onChange={(opta_code) => setPlayerInSquad(8, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[8].locked} onChange={(e) => setLockPlayerInSquad(8, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="MID" onChange={(opta_code) => setPlayerInSquad(9, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[9].locked} onChange={(e) => setLockPlayerInSquad(9, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="MID" onChange={(opta_code) => setPlayerInSquad(10, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[10].locked} onChange={(e) => setLockPlayerInSquad(10, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="MID" onChange={(opta_code) => setPlayerInSquad(11, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[11].locked} onChange={(e) => setLockPlayerInSquad(11, e)} /> Locked
                    </div>
                    <div>
                        FWDs
                        <PlayerSearchInput players={players} preSetPosition="FWD" onChange={(opta_code) => setPlayerInSquad(12, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[12].locked} onChange={(e) => setLockPlayerInSquad(12, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="FWD" onChange={(opta_code) => setPlayerInSquad(13, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[13].locked} onChange={(e) => setLockPlayerInSquad(13, e)} /> Locked
                        <PlayerSearchInput players={players} preSetPosition="FWD" onChange={(opta_code) => setPlayerInSquad(14, opta_code)}/>
                        <input type="checkbox" checked={existingSquad[14].locked} onChange={(e) => setLockPlayerInSquad(14, e)} /> Locked
                    </div>
                </div>

                <input type="submit" value="Optimize" />
            </form>
            <div> ----------Optimized Squad----------</div>
            <OptimizeResult squad={enrichedSquad} />
        </div>
    );
}
