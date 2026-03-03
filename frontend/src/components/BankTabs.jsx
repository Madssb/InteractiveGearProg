export default function BankTabs({ header, activeTabId, onTabChange }) {
    return (
        <div id="bank-tabs-section">
            <div className="bank-tabs-corner"></div>
            {header.map((tab) => (
                <button
                    key={tab.id}
                    type="button"
                    className={`bank-tab-button ${activeTabId === tab.id ? "active" : ""}`}
                    onClick={() => onTabChange(tab.id)}
                    aria-label={`Open bank tab ${tab.id}`}
                >
                    <img src={tab.imgUrl} alt="" />
                </button>
            ))}
            <div className="bank-tabs-corner"></div>
        </div>
    );
}
