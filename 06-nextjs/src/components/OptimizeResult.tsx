//Optimized Squad result component. 
//Version: 1.0.0

import { EnrichedPlayer } from "@/lib/enrichment";
type Props = {
    squad: EnrichedPlayer[];
};

export default function OptimizeResult({squad}: Props) {
    return (
        <div>
            <ul>
                {squad.map(p => (
                            <li key={p.opta_code}>
                                {p.name} — {p.club_short} {p.position} £{p.price} Expected Points{p.expected_pts.map(ep => ` GW${ep.gw}: ${ep.pts}`)}
                            </li>
                ))}
            </ul>
        </div>
    )
}