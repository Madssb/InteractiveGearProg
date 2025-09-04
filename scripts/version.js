/**
 * Syncs populates span with version id with latest version text for syncing index.html and changelog.html.
 */
function init() {
    fetch('/pages/changelog.html')
        .then(response => {
            // When the page is loaded convert it to text
            return response.text()
        })
        .then(html => {
            // Initialize the DOM parser
            const parser = new DOMParser()

            // Parse the text
            const doc = parser.parseFromString(html, "text/html")
            // top h2 always represents latest version.
            const latest_version_text = doc.querySelector('h2').innerHTML.toLowerCase()



            console.log(latest_version_text)
            let span = document.querySelector("#version");
            span.textContent = latest_version_text
            console.log(span.textContent)



        })
        .catch(error => {
            console.error('Failed to fetch page: ', error)
        })
}
// Start rendering when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", init);