import BackHome from "../components/BackHome"

function PrivacyPage(){
    return (
        <>
            <h1>Privacy Policy</h1>
            <p>This website uses GoatCounter to track basic, non-personal data such as page views and referral sources. No
                personal data is collected or stored, and GoatCounter does not use cookies.</p>

            <p>GoatCounter is a privacy-focused analytics tool that complies with GDPR and other privacy regulations. For more
                information, you can visit their{" "}
                <a href="https://www.goatcounter.com/privacy" target="_blank">privacy policy</a>.
            </p>

            <h2>Use of Local Storage</h2>
            <p>This website uses local storage to enhance your experience by remembering your preferences, such as dark mode
                settings and progress tracking. Local storage allows this data to be stored on your device, so you don't lose
                your settings between sessions.</p>

            <p>No personal information is stored or shared, and this data remains entirely within your browser. Local storage is
                only used to improve functionality and does not track or share your activity with third parties.</p>
            <BackHome />
        </>
    )
}
export default PrivacyPage