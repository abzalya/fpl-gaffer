"use client";

import { useState, useEffect } from "react";

export function useCountdown(deadline: string): string {
    const [label, setLabel] = useState("");

    useEffect(() => {
        function compute() {
            const diff = new Date(deadline).getTime() - Date.now();
            if (diff <= 0) return "Deadline passed";
            const d = Math.floor(diff / 86400000);
            const h = Math.floor((diff % 86400000) / 3600000);
            const m = Math.floor((diff % 3600000) / 60000);
            return `${d}d ${h}h ${m}m`;
        }

        setLabel(compute());
        const id = setInterval(() => setLabel(compute()), 60000);
        return () => clearInterval(id);
    }, [deadline]);

    return label;
}
