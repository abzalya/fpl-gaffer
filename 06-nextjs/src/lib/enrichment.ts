// Function to join the optimize response with the cached players information. 
import { PlayerResponse, SquadResponse } from "@/lib/api";

export type EnrichedPlayer = SquadResponse & Omit<PlayerResponse, "name" | "club" | "price" | "position" | "opta_code">;

export function enrichSquad(squad: SquadResponse[], players: PlayerResponse[]): EnrichedPlayer[] {
    const playerMap = new Map(players.map(p => [p.opta_code, p]));
    return squad.map(s => {
        const info = playerMap.get(s.opta_code);
        return { ...s, ...info } as EnrichedPlayer;
    });
}
