// API Fetches & Logic
// Version: 1.0.0

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Defining Types of API responses (similar to contracts in 05-api)
export type GameweekResponse = {
    gameweek_id: number;
    name: string;
    deadline: string;
    is_next: boolean;
};

export type FixtureResponse = {
    horizon: number;
    is_home: boolean | null;
    opponent: string;
    difficulty: number | null;
};

export type PlayerResponse = {
    opta_code: number;
    name: string;
    club: string;
    club_short: string;
    position: string;
    price: number;
    status: string;
    predicted_pts_h1: number | null;
    predicted_pts_h2: number | null;
    predicted_pts_h3: number | null;
    fixtures: FixtureResponse[];
};

export type PointsResponse = {
    gw: number;
    pts: number;
};

export type SquadResponse = {
    club: string;
    name: string;
    price: number;
    position: string;
    opta_code: number;
    is_captain: boolean;
    is_starter: boolean;
    expected_pts: PointsResponse[];
};

export type TransferResponse = {
    club: string;
    name: string;
    price: number;
    position: string;
    opta_code: number;    
};

export type OptimizeResponse = {
    status: string;
    horizon: number;
    solve_time_ms: number;
    error_message: string | null;
    squad: { squad: SquadResponse[] };
    transfers_in: { transfers: TransferResponse[] } | null;
    transfers_out: { transfers: TransferResponse[] } | null;
};

export type SquadRequest= {
    opta_code: number;
    locked: boolean;
};

export type ChipsRequest = {
    wildcard: boolean;
    free_hit: boolean;
    bench_boost: boolean;
    triple_captain: boolean;
};

export type OptimizeRequest = {
    existing_squad: SquadRequest[] | null;
    chips: ChipsRequest;
    bank: number;
    free_transfers: number;
    horizon: number;
};

export async function getPlayers(): Promise<PlayerResponse[]> {
    const response = await fetch(`${API_URL}/players`, {next: {revalidate: 43200}});
    if (!response.ok) throw new Error(`Failed to fetch players: ${response.status}`);
    return response.json();
}
export async function getNextGameweek(): Promise<GameweekResponse> {
    const response = await fetch(`${API_URL}/gameweek/next`, {next: {revalidate: 43200}});
    if (!response.ok) throw new Error(`Failed to fetch gameweek: ${response.status}`);
    return response.json();
}
export async function postOptimize(req: OptimizeRequest): Promise<OptimizeResponse> {
    const response = await fetch(`${API_URL}/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
    });
    if (!response.ok) throw new Error(`Failed to optimize squad: ${response.status}`);
    return response.json();
}
