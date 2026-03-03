const LEFTMOST_TAB_ICON = "/images/bank/infinity_symbol.png";

export default function BankTabs({ header, activeTabId, onTabChange }) {
    return (
        <div id="bank-tabs-section">
            <div className="bank-tabs-corner"></div>
            {header.map((tab, index) => (
                <button
                    key={tab.id}
                    type="button"
                    className={`bank-tab-button ${activeTabId === tab.id ? "active" : ""}`}
                    onClick={() => onTabChange(tab.id)}
                    aria-label={`Open bank tab ${tab.id}`}
                >
                    <img src={index === 0 ? LEFTMOST_TAB_ICON : tab.imgUrl} alt="" />
                </button>
            ))}
            <div className="bank-tabs-corner"></div>
        </div>
    );
}
