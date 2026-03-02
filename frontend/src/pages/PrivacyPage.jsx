import Footer from "@/components/static/Footer"

export default function PrivacyPage(){
    return (
        <>
            <h1>Privacy Policy</h1>
            <p>This website uses privacy-focused analytics and infrastructure logs to understand usage, keep the service healthy,
                and protect against abuse.</p>

            <h2>GoatCounter Analytics</h2>
            <p>This website uses GoatCounter to track basic aggregate data such as page views and referral sources. GoatCounter
                does not use cookies for this site.</p>
            <p>For more information, you can visit their{" "}
                <a href="https://www.goatcounter.com/privacy" target="_blank">privacy policy</a>.
            </p>

            <h2>Cloudflare Processing</h2>
            <p>Traffic to this site and API is routed through Cloudflare for security and reliability. Cloudflare may process
                request metadata (for example IP address, user agent, and request path) to provide DDoS protection, caching,
                routing, and operational analytics.</p>

            <h2>Backend Service Metrics</h2>
            <p>The API records daily aggregated endpoint usage counts (for example how many times each endpoint is called per
                day). These metrics are stored as totals and are used for capacity planning and service improvements.</p>

            <h2>Data Minimization</h2>
            <p>We avoid collecting unnecessary personal data. For usage analytics, we store aggregate counts rather than full
                request payloads. Shared chart links store only the chart data needed to load the shared chart.</p>

            <h2>Use of Local Storage</h2>
            <p>This website uses local storage to enhance your experience by remembering preferences and progress. Local storage
                keeps this data in your browser so you do not lose settings between sessions.</p>

            <p>No personal information from local storage is sent to third parties by default. Local storage is used to improve
                functionality and user experience.</p>

            <p>If you have privacy concerns, contact the maintainer via the project repository.</p>
            <Footer />
        </>
    )
}
