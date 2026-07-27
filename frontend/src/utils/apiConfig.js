const API_ENV_NAME = "VITE_API_BASE_URL";

function warnApiDisabled(message, error) {
    if (!import.meta.env.DEV) return;
    if (error) {
        console.warn(`API disabled: ${message}`, error);
        return;
    }
    console.warn(`API disabled: ${message}`);
}

function optionalApiBaseUrl() {
    const raw = import.meta.env[API_ENV_NAME];

    if (typeof raw !== "string" || raw.trim() === "") {
        warnApiDisabled(`set ${API_ENV_NAME} to enable API-backed features.`);
        return null;
    }

    let parsed;
    try {
        parsed = new URL(raw);
    } catch (error) {
        warnApiDisabled(`API base URL must be a valid absolute URL. Received: ${raw}`, error);
        return null;
    }

    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
        warnApiDisabled(`API base URL must start with http:// or https://. Received: ${raw}`);
        return null;
    }

    if (parsed.search || parsed.hash) {
        warnApiDisabled(`API base URL must not include a query string or hash. Received: ${raw}`);
        return null;
    }

    return raw.trim().replace(/\/+$/, "");
}

export const API_BASE_URL = optionalApiBaseUrl();
export const API_CONFIGURED = Boolean(API_BASE_URL);

export function apiUrl(path) {
    if (!API_BASE_URL) return null;
    return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}
