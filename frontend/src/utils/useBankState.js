import { useEffect, useState } from "react";
import { BANK_API_URL, POLL_INTERVAL_MS, normalizeBankPayload } from "@/utils/bankPayload";

export default function useBankState(fallbackBank) {
    const [bankState, setBankState] = useState(fallbackBank);
    const [lastSyncedAt, setLastSyncedAt] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        let cancelled = false;

        async function fetchBankState() {
            try {
                const response = await fetch(BANK_API_URL, { method: "GET" });
                if (!response.ok) throw new Error(`status ${response.status}`);
                const payload = await response.json();
                const normalized = normalizeBankPayload(payload);
                if (!normalized) throw new Error("Unexpected bank payload shape");
                if (cancelled) return;
                setBankState(normalized);
                setError("");
                setLastSyncedAt(new Date());
            } catch (fetchError) {
                if (cancelled) return;
                console.error(fetchError);
                setError("Live bank sync unavailable. Showing fallback data.");
            }
        }

        fetchBankState();
        const intervalId = setInterval(fetchBankState, POLL_INTERVAL_MS);
        return () => {
            cancelled = true;
            clearInterval(intervalId);
        };
    }, [fallbackBank]);

    return { bankState, lastSyncedAt, error };
}
