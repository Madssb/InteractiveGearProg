const API_BASE_URL_BY_FRONTEND_HOST = {
    "127.0.0.1": "http://127.0.0.1:8000",
    localhost: "http://127.0.0.1:8000",
    "::1": "http://127.0.0.1:8000",
    "ladlorchart.com": "https://api.ladlorchart.com",
};

function warnApiDisabled(message, error) {
    if (!import.meta.env.DEV) return;
    if (error) {
        console.warn(`API disabled: ${message}`, error);
        return;
    }
    console.warn(`API disabled: ${message}`);
}

function derivedApiBaseUrl() {
    if (typeof window === "undefined") {
        warnApiDisabled("window.location is unavailable.");
        return null;
    }

    const frontendHost = window.location.hostname.toLowerCase();
    const apiBaseUrl = API_BASE_URL_BY_FRONTEND_HOST[frontendHost];

    if (!apiBaseUrl) {
        warnApiDisabled(`no API mapping exists for frontend host ${frontendHost}.`);
        return null;
    }

    return apiBaseUrl;
}

export const API_BASE_URL = derivedApiBaseUrl();
export const API_CONFIGURED = Boolean(API_BASE_URL);

export function apiUrl(path) {
    if (!API_BASE_URL) return null;
    return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}
