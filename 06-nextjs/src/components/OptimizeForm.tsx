// crating the post optimize component
"use client";

import React, {useState} from "react";
import {postOptimize} from "@/lib/api";

export default function OptimizeForm() {
    const [horizon, setHorizon] = useState(3);
    const [bank, setBank] = useState(0);
    const [freeTransfers, setFreeTransfers] = useState(0);
    const [wildcard, setWildcard] = useState(false);
    const [freeHit, setFreeHit] = useState(false);
    const [benchBoost, setBenchBoost] = useState(false);
    const [tripleCaptain, setTripleCaptain] = useState(false);
    const [existingSquad, setExistingSquad] = useState<{ opta_code: number | null; locked: boolean }[]>(
        Array(15).fill(null).map(() => ({ opta_code: null, locked: false }))
    );
    const [optimizeResult, setOptimizeResult] = useState<null | object>(null);

    const setPlayerInSquad = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
        const updatedSquad = [...existingSquad];
        updatedSquad[index] = {...updatedSquad[index], opta_code: Number(e.target.value)};
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
            bank: bank,
            free_transfers: freeTransfers,
            horizon: horizon,
        });
        setOptimizeResult(response);
    }

    return (
    <form onSubmit={handleSubmit}>
        <div> FORM Testing</div>
        <input type="text" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} />
        <input type="text" value={bank} onChange={(e) => setBank(Number(e.target.value))} />
        <input type="text" value={freeTransfers} onChange={(e) => setFreeTransfers(Number(e.target.value))} />
        <div>
            <input type="checkbox" checked={wildcard} onChange={(e) => setWildcard(e.target.checked)} /> Wildcard
            <input type="checkbox" checked={freeHit} onChange={(e) => setFreeHit(e.target.checked)} /> Free Hit
            <input type="checkbox" checked={benchBoost} onChange={(e) => setBenchBoost(e.target.checked)} /> Bench Boost
            <input type="checkbox" checked={tripleCaptain} onChange={(e) => setTripleCaptain(e.target.checked)} /> Triple Captain
        </div>
        <div> existing squad 
            <div>
                GK
                <input type="text" placeholder="GK 1" value={existingSquad[0].opta_code ?? ""} onChange={(e) => setPlayerInSquad(0, e)}/>
                <input type="checkbox" checked={existingSquad[0].locked} onChange={(e) => setLockPlayerInSquad(0, e)} /> Locked
                <input type="text" placeholder="GK 2" value={existingSquad[1].opta_code ?? ""} onChange={(e) => setPlayerInSquad(1, e)}/>
                <input type="checkbox" checked={existingSquad[1].locked} onChange={(e) => setLockPlayerInSquad(1, e)} /> Locked
            </div>
            <div>
                DEF
                <input type="text" placeholder="DEF 1" value={existingSquad[2].opta_code ?? ""} onChange={(e) => setPlayerInSquad(2, e)}/>
                <input type="checkbox" checked={existingSquad[2].locked} onChange={(e) => setLockPlayerInSquad(2, e)} /> Locked
                <input type="text" placeholder="DEF 2" value={existingSquad[3].opta_code ?? ""} onChange={(e) => setPlayerInSquad(3, e)}/>
                <input type="checkbox" checked={existingSquad[3].locked} onChange={(e) => setLockPlayerInSquad(3, e)} /> Locked
                <input type="text" placeholder="DEF 3" value={existingSquad[4].opta_code ?? ""} onChange={(e) => setPlayerInSquad(4, e)}/>
                <input type="checkbox" checked={existingSquad[4].locked} onChange={(e) => setLockPlayerInSquad(4, e)} /> Locked
                <input type="text" placeholder="DEF 4" value={existingSquad[5].opta_code ?? ""} onChange={(e) => setPlayerInSquad(5, e)}/>
                <input type="checkbox" checked={existingSquad[5].locked} onChange={(e) => setLockPlayerInSquad(5, e)} /> Locked
                <input type="text" placeholder="DEF 5" value={existingSquad[6].opta_code ?? ""} onChange={(e) => setPlayerInSquad(6, e)}/>
                <input type="checkbox" checked={existingSquad[6].locked} onChange={(e) => setLockPlayerInSquad(6, e)} /> Locked
            </div>
            <div>
                MID
                <input type="text" placeholder="MID 1" value={existingSquad[7].opta_code ?? ""} onChange={(e) => setPlayerInSquad(7, e)}/>
                <input type="checkbox" checked={existingSquad[7].locked} onChange={(e) => setLockPlayerInSquad(7, e)} /> Locked
                <input type="text" placeholder="MID 2" value={existingSquad[8].opta_code ?? ""} onChange={(e) => setPlayerInSquad(8, e)}/>
                <input type="checkbox" checked={existingSquad[8].locked} onChange={(e) => setLockPlayerInSquad(8, e)} /> Locked
                <input type="text" placeholder="MID 3" value={existingSquad[9].opta_code ?? ""} onChange={(e) => setPlayerInSquad(9, e)}/>
                <input type="checkbox" checked={existingSquad[9].locked} onChange={(e) => setLockPlayerInSquad(9, e)} /> Locked
                <input type="text" placeholder="MID 4" value={existingSquad[10].opta_code ?? ""} onChange={(e) => setPlayerInSquad(10, e)}/>
                <input type="checkbox" checked={existingSquad[10].locked} onChange={(e) => setLockPlayerInSquad(10, e)} /> Locked
                <input type="text" placeholder="MID 5" value={existingSquad[11].opta_code ?? ""} onChange={(e) => setPlayerInSquad(11, e)}/>
                <input type="checkbox" checked={existingSquad[11].locked} onChange={(e) => setLockPlayerInSquad(11, e)} /> Locked
            </div>
            <div>
                FWD
                <input type="text" placeholder="FWD 1" value={existingSquad[12].opta_code ?? ""} onChange={(e) => setPlayerInSquad(12, e)}/>
                <input type="checkbox" checked={existingSquad[12].locked} onChange={(e) => setLockPlayerInSquad(12, e)} /> Locked
                <input type="text" placeholder="FWD 2" value={existingSquad[13].opta_code ?? ""} onChange={(e) => setPlayerInSquad(13, e)}/>
                <input type="checkbox" checked={existingSquad[13].locked} onChange={(e) => setLockPlayerInSquad(13, e)} /> Locked
                <input type="text" placeholder="FWD 3" value={existingSquad[14].opta_code ?? ""} onChange={(e) => setPlayerInSquad(14, e)}/>
                <input type="checkbox" checked={existingSquad[14].locked} onChange={(e) => setLockPlayerInSquad(14, e)} /> Locked
            </div>
        </div>
        
        <input type="submit" value="Optimize" />
    </form>
    );
}
