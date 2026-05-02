"use client";

import { useState } from "react";
import { postOptimize, OptimizeRequest, OptimizeResponse, PlayerResponse, TransferResponse } from "@/lib/api";
import { enrichSquad, EnrichedPlayer } from "@/lib/enrichment";

type Result = {
    raw: OptimizeResponse;
    squad: EnrichedPlayer[];
    transferInCodes: Set<number>;
    transferOutCodes: Set<number>;
    transfersIn: TransferResponse[];
    transfersOut: TransferResponse[];
};

export function useOptimise(players: PlayerResponse[]) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<Result | null>(null);

    async function run(req: OptimizeRequest): Promise<boolean> {
        setLoading(true);
        setError(null);
        try {
            const raw = await postOptimize(req);
            const squad = enrichSquad(raw.squad.squad, players);
            const transfersIn = raw.transfers_in?.transfers ?? [];
            const transfersOut = raw.transfers_out?.transfers ?? [];
            const transferInCodes = new Set(transfersIn.map(t => t.opta_code));
            const transferOutCodes = new Set(transfersOut.map(t => t.opta_code));
            setResult({ raw, squad, transferInCodes, transferOutCodes, transfersIn, transfersOut });
            return true;
        } catch (e) {
            setError(e instanceof Error ? e.message : "Optimisation failed");
            return false;
        } finally {
            setLoading(false);
        }
    }

    function reset() {
        setResult(null);
        setError(null);
    }

    return { loading, error, result, run, reset };
}
