const isLocalFrontend = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const DEFAULT_API_BASE_URL = import.meta.env.DEV || isLocalFrontend
    ? "http://127.0.0.1:8000"
    : "https://api.ladlorchart.com";

export const API_BASE_URL = (
    import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL
).replace(/\/$/, "");

export function apiUrl(path) {
    return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}
