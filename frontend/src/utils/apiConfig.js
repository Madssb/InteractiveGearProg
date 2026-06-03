function requiredApiBaseUrl() {
    const raw = import.meta.env.VITE_API_BASE_URL;
    if (typeof raw !== "string" || raw.trim() === "") {
        throw new Error("VITE_API_BASE_URL is required. Set it to an absolute http:// or https:// API base URL.");
    }

    let parsed;
    try {
        parsed = new URL(raw);
    } catch (error) {
        throw new Error(`VITE_API_BASE_URL must be a valid absolute URL. Received: ${raw}`, { cause: error });
    }

    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
        throw new Error(`VITE_API_BASE_URL must start with http:// or https://. Received: ${raw}`);
    }

    if (parsed.search || parsed.hash) {
        throw new Error(`VITE_API_BASE_URL must not include a query string or hash. Received: ${raw}`);
    }

    return raw.trim().replace(/\/+$/, "");
}

export const API_BASE_URL = requiredApiBaseUrl();

export function apiUrl(path) {
    return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}
