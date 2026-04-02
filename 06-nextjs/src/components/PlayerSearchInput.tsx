//input component for player search. 
"use client";

import {useState} from "react";
import {PlayerResponse} from "@/lib/api";

type Props = {
    players: PlayerResponse[];
    preSetPosition: string;
    onChange: (opta_code: number) => void;
};

export default function PlayerSearchInput({players, preSetPosition, onChange}: Props) {
    const [query, setQuery] = useState("");

    return (
        <div>
            <input value={query} onChange={(e) => setQuery(e.target.value)}/>
            {query.length > 0 && (
                <ul>
                    {players
                        .filter(p => p.name.toLowerCase().includes(query.toLowerCase()) && p.position === preSetPosition)
                        .map(p => (
                            <li key={p.opta_code} onClick={() => { onChange(p.opta_code); setQuery(p.name); }}>
                                {p.name} — {p.club_short} {p.position} £{p.price}
                            </li>
                        ))
                    }
                </ul>
            )}
        </div>
    );
}
