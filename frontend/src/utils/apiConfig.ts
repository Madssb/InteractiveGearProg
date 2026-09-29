const API_BASE_URL_BY_FRONTEND_HOST = {
    "127.0.0.1": "http://127.0.0.1:8000",
    localhost: "http://127.0.0.1:8000",
    "::1": "http://127.0.0.1:8000",
    "ladlorchart.com": "https://api.ladlorchart.com",
};

/**
 * Get Full api endpoint url.
 * @param path Endpoint path.
 * @returns Full api endpoint url.
 * @throws {Error} If the frontend host is unsupported.
 */
export function apiUrl(path: string): string {
    if (typeof window === "undefined") {
        throw new Error("window is undefined; required for deriving correct api base url.")
    }
    const frontendHost = window.location.hostname.toLowerCase();
    // @ts-ignore
    const apiBaseUrl = API_BASE_URL_BY_FRONTEND_HOST[frontendHost];

    if (!apiBaseUrl) throw new Error(`Unsupported frontend host: ${frontendHost}`);
    
    return `${apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}
