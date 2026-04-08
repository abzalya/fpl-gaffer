// Optimize Summary component
// Version: 1.0.0
import { OptimizeResponse, TransferResponse } from "@/lib/api";
import { EnrichedPlayer } from "@/lib/enrichment";

type Props = {
    optimizeResponse: OptimizeResponse[];
    squad: EnrichedPlayer[];
    bankInput: number;
};

function getCaptainForGW(squad: EnrichedPlayer[], gw: number, horizonIndex: number) {
    if (horizonIndex === 1) {
        // GW1: find the player with is_captain flag
        let captain = null;
        for (const player of squad) {
            if (player.is_captain) {
                captain = player;
                break;
            }
        }
        if (captain === null) {
            return { player: null, fixture: null };
        }
        let fixture = null;
        for (const f of captain.fixtures) {
            if (f.horizon === horizonIndex) {
                fixture = f;
                break;
            }
        }
        return { player: captain, fixture };
    }

    // GW2+: find the starter with the highest expected points for this GW
    const starters = squad.filter(p => p.is_starter);
    let captain = null;
    let bestPts = -Infinity;
    for (const player of starters) {
        let pts = 0;
        for (const ep of player.expected_pts) {
            if (ep.gw === gw) {
                pts = ep.pts;
                break;
            }
        }
        if (pts > bestPts) {
            bestPts = pts;
            captain = player;
        }
    }
    if (captain === null) {
        return { player: null, fixture: null };
    }
    let fixture = null;
    for (const f of captain.fixtures) {
        if (f.horizon === horizonIndex) {
            fixture = f;
            break;
        }
    }
    return { player: captain, fixture };
}

export default function OptimizeSummary({ optimizeResponse, squad, bankInput }: Props) {
    const first = optimizeResponse[0];

    //TRANSFERS
    let transfersIn: TransferResponse[] | null = null;
    let transfersOut: TransferResponse[] | null = null;

    if (first !== undefined) {
        if (first.transfers_in !== null) {
            transfersIn = first.transfers_in.transfers;
        }
        if (first.transfers_out !== null) {
            transfersOut = first.transfers_out.transfers;
        }
    }

    const hasTransfers = transfersIn !== null || transfersOut !== null;

    //BANK
    let inCost = 0;
    if (transfersIn !== null) {
        for (const p of transfersIn) {
            inCost += p.price;
        }
    }
    let outCost = 0;
    if (transfersOut !== null) {
        for (const p of transfersOut) {
            outCost += p.price;
        }
    }
    const transferCost = inCost - outCost;
    const newBank = bankInput - transferCost;

    //CAPTAINS
    const gwSet = new Set<number>();
    for (const player of squad) {
        for (const ep of player.expected_pts) {
            gwSet.add(ep.gw);
        }
    }
    const gwNumbers = Array.from(gwSet).sort((a, b) => a - b);

    const captains = [];
    for (let index = 0; index < gwNumbers.length; index++) {
        const gw = gwNumbers[index];
        const horizonIndex = index + 1;
        const { player, fixture } = getCaptainForGW(squad, gw, horizonIndex);
        captains.push({ gw, player, fixture });
    }

    //RENDERING
    function renderTransfersIn() {
        if (transfersIn === null || transfersIn.length === 0) {
            return <p>No transfers in</p>;
        }
        return (
            <ul>
                {transfersIn.map(p => (
                    <li key={p.opta_code}>
                        {p.name} — {p.club} {p.position} £{p.price}m
                    </li>
                ))}
            </ul>
        );
    }

    function renderTransfersOut() {
        if (transfersOut === null || transfersOut.length === 0) {
            return <p>No transfers out</p>;
        }
        return (
            <ul>
                {transfersOut.map(p => (
                    <li key={p.opta_code}>
                        {p.name} — {p.club} {p.position} £{p.price}m
                    </li>
                ))}
            </ul>
        );
    }

    function renderTransfersSection() {
        if (!hasTransfers) {
            return (
                <div>
                    <h4>Proposed Squad</h4>
                    <ul>
                        {squad.map(p => (
                            <li key={p.opta_code}>
                                {p.name} — {p.club_short} {p.position} £{p.price}m
                            </li>
                        ))}
                    </ul>
                </div>
            );
        }
        return (
            <div style={{ display: "flex", gap: "2rem" }}>
                <div>
                    <h4>In</h4>
                    {renderTransfersIn()}
                </div>
                <div>
                    <h4>Out</h4>
                    {renderTransfersOut()}
                </div>
            </div>
        );
    }

    function renderCaptainRow(gw: number, player: EnrichedPlayer | null, fixture: { opponent: string; is_home: boolean | null } | null) {
        let playerName = "Unknown";
        if (player !== null) {
            playerName = player.name;
        }
        let opponent = "?";
        if (fixture !== null) {
            opponent = fixture.opponent;
        }
        let homeAway = "?";
        if (fixture !== null) {
            if (fixture.is_home === true) {
                homeAway = "H";
            } else {
                homeAway = "A";
            }
        }
        return (
            <li key={gw}>
                GW{gw} — {playerName} vs {opponent} ({homeAway})
            </li>
        );
    }

    return (
        <div>
            {/* SECTION 1: TRANSFERS */}
            <section>
                <h3>Transfers</h3>
                {renderTransfersSection()}
            </section>

            {/* SECTION 2: BANK */}
            <section>
                <h3>Bank</h3>
                <p>
                    £{bankInput.toFixed(1)}m → £{newBank.toFixed(1)}m (cost: £{transferCost.toFixed(1)}m)
                </p>
            </section>

            {/* SECTION 3: CAPTAINS */}
            <section>
                <h3>Captains</h3>
                <ul>
                    {captains.map(({ gw, player, fixture }) => renderCaptainRow(gw, player, fixture))}
                </ul>
            </section>
        </div>
    );
}

//Need to make it one or the other with the raw result. 
//checkbox ?
//checked = summary rendered  
