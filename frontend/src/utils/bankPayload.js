export const BANK_API_URL = "https://api.ladlorchart.com/bank/"; // Remote
export const POLL_INTERVAL_MS = 5 * 60 * 1000;
export const ACTIVE_TAB_KEY = "active-bank-tab-id";

function normalizeLegacyTabMap(tabMap) {
    if (!tabMap || typeof tabMap !== "object") return [];
    return Object.entries(tabMap).map(([name, info]) => ({
        name,
        quantity: Number(info.quantity ?? 1),
        imgUrl: info.imgUrl ?? ""
    }));
}

export function normalizeBankPayload(raw) {
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

export function getTabIdFromStorage(defaultId) {
    const saved = localStorage.getItem(ACTIVE_TAB_KEY);
    return saved || defaultId;
}
