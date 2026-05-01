import Footer from "@/components/static/Footer"

export default function PrivacyPage(){
    return (
        <>
            <h1>Privacy Policy</h1>
            <p>Last updated: May 1, 2026</p>

            <p>This website stores the data needed to run the chart tools, shared links, lightweight usage metrics, and abuse
                protection.</p>

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
            <p>The API stores a timestamped entry each time an endpoint is called. These entries are used to understand which
                parts of the service are used and to keep the backend reliable.</p>

            <p>Separately, operational logs may include request details such as the method, path, status code, response time,
                host, and client IP information. These logs are used for debugging, monitoring, and abuse protection.</p>

            <h2>Chart and Progress Data</h2>
            <p>Shared chart links store the milestone sequence needed to load that shared chart. The share token is random and
                is used only to retrieve the saved chart data.</p>

            <p>The chart page may submit a progress snapshot containing the milestone names marked complete in the browser. This
                is used to understand milestone completion patterns and improve the chart.</p>

            <p>Backend data is stored in PostgreSQL on infrastructure maintained for this service.</p>

            <h2>Data Minimization</h2>
            <p>We avoid collecting unnecessary personal data. Shared chart links store only the chart data needed to load the
                shared chart. Progress snapshots store completed milestone names, not account profiles.</p>

            <h2>Use of Local Storage</h2>
            <p>This website uses local storage to remember preferences, selected tabs, migration state, and milestone progress.
                Local storage keeps this data in your browser so you do not lose settings between sessions.</p>

            <p>Some locally stored milestone progress may be submitted to this service as described above. Local storage is used
                to improve functionality and user experience.</p>

            <h2>Retention</h2>
            <p>Shared chart data, endpoint usage records, progress snapshots, and operational logs are currently kept
                indefinitely. This may change if a retention schedule is added later.</p>

            <p>If you have privacy questions or want to request deletion of data associated with a shared chart link, contact
                the maintainer through the project repository.</p>
            <Footer />
        </>
    )
}
