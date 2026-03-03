import BankItem from "@/components/BankItem";
import Footer from "@/components/static/Footer";
import "@/styles/bank.css";
import { useEffect, useMemo, useState } from "react";

const BANK_API_URL = "https://api.ladlorchart.com/bank/"; // Remote
// const BANK_API_URL = "http://127.0.0.1:8000/bank/"; // Localhost testing
const POLL_INTERVAL_MS = 5 * 60 * 1000;
const ACTIVE_TAB_KEY = "active-bank-tab-id";

const FALLBACK_BANK = {
    title: "The Bank of Ladlor",
    header: [
        { id: "0", imgUrl: "https://oldschool.runescape.wiki/images/Infinity_symbol.png" },
        { id: "1", imgUrl: "https://oldschool.runescape.wiki/images/Crystal_helm.png" },
        { id: "2", imgUrl: "https://oldschool.runescape.wiki/images/Amulet_of_glory(4).png" }
    ],
    tabs: {
        "0": [
            {
                name: "Abyssal whip",
                quantity: 1,
                imgUrl: "https://oldschool.runescape.wiki/images/Abyssal_whip.png",
                wikiUrl: "https://oldschool.runescape.wiki/w/Abyssal_whip"
            },
            {
                name: "Blood rune",
                quantity: 45000,
                imgUrl: "https://oldschool.runescape.wiki/images/Blood_rune.png",
                wikiUrl: "https://oldschool.runescape.wiki/w/Blood_rune"
            }
        ],
        "1": [],
        "2": []
    }
};

function normalizeLegacyTabMap(tabMap) {
    if (!tabMap || typeof tabMap !== "object") return [];
    return Object.entries(tabMap).map(([name, info]) => ({
        name,
        quantity: Number(info.quantity ?? 1),
        imgUrl: info.imgUrl ?? "",
        wikiUrl: info.wikiUrl ?? ""
    }));
}

function normalizeBankPayload(raw) {
    if (!raw || typeof raw !== "object") return null;

    if (Array.isArray(raw.header) && raw.tabs && typeof raw.tabs === "object") {
        return raw;
    }

    if (raw.header && typeof raw.header === "object") {
        const header = Object.entries(raw.header).map(([id, imgUrl]) => ({ id, imgUrl }));
        const tabs = {};
        Object.entries(raw).forEach(([key, value]) => {
            if (!key.startsWith("tab")) return;
            const id = key.replace("tab", "");
            tabs[id] = normalizeLegacyTabMap(value);
        });
        return {
            title: raw.title || "The Bank of Ladlor",
            header,
            tabs
        };
    }

    return null;
}

function readInitialActiveTab(defaultId) {
    const saved = localStorage.getItem(ACTIVE_TAB_KEY);
    return saved || defaultId;
}

export default function BankPage() {
    const [bankState, setBankState] = useState(FALLBACK_BANK);
    const [activeTabId, setActiveTabId] = useState(readInitialActiveTab(FALLBACK_BANK.header[0]?.id ?? "0"));
    const [lastSyncedAt, setLastSyncedAt] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        localStorage.setItem(ACTIVE_TAB_KEY, activeTabId);
    }, [activeTabId]);

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
                if (!normalized.tabs[activeTabId]) {
                    setActiveTabId(normalized.header[0]?.id ?? "0");
                }
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
    }, [activeTabId]);

    const visibleItems = useMemo(() => bankState.tabs[activeTabId] || [], [bankState, activeTabId]);

    return (
        <>
            <div className="bank-page">
                <div id="bank">
                    <div id="bank-title-section"><span>{bankState.title || "The Bank of Ladlor"}</span></div>
                    <div id="margin"></div>
                    <div id="bank-main-section">
                        <div id="bank-tabs-section">
                            <div className="bank-tabs-corner"></div>
                            {bankState.header.map((tab) => (
                                <button
                                    key={tab.id}
                                    type="button"
                                    className={`bank-tab-button ${activeTabId === tab.id ? "active" : ""}`}
                                    onClick={() => setActiveTabId(tab.id)}
                                    aria-label={`Open bank tab ${tab.id}`}
                                >
                                    <img src={tab.imgUrl} alt="" />
                                </button>
                            ))}
                            <div className="bank-tabs-corner"></div>
                        </div>
                        <div id="bank-items-section">
                            {visibleItems.map((item) => <BankItem key={item.name} item={item} />)}
                        </div>
                    </div>
                </div>
                {error && <p className="bank-status bank-error">{error}</p>}
                {lastSyncedAt && <p className="bank-status">Last synced: {lastSyncedAt.toLocaleString()}</p>}
            </div>
            <Footer />
        </>
    );
}
