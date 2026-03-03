import BankItem from "@/components/BankItem";
import BankTabs from "@/components/BankTabs";
import Footer from "@/components/static/Footer";
import fallbackBank from "@/data/bank-default.json";
import "@/styles/bank.css";
import { ACTIVE_TAB_KEY, getTabIdFromStorage } from "@/utils/bankPayload";
import useBankState from "@/utils/useBankState";
import { useEffect, useMemo, useState } from "react";

export default function BankPage() {
    const { bankState, lastSyncedAt, error } = useBankState(fallbackBank);
    const [activeTabId, setActiveTabId] = useState(() =>
        getTabIdFromStorage(fallbackBank.header[0]?.id ?? "0")
    );

    useEffect(() => {
        localStorage.setItem(ACTIVE_TAB_KEY, activeTabId);
    }, [activeTabId]);

    useEffect(() => {
        if (bankState.tabs[activeTabId]) return;
        setActiveTabId(bankState.header[0]?.id ?? "0");
    }, [bankState, activeTabId]);

    const visibleItems = useMemo(
        () => bankState.tabs[activeTabId] || [],
        [bankState, activeTabId]
    );

    return (
        <>
            <div className="bank-page">
                <div id="bank">
                    <div id="bank-title-section">
                        <span>{bankState.title || "The Bank of Ladlor"}</span>
                    </div>
                    <div id="margin"></div>
                    <div id="bank-main-section">
                        <BankTabs
                            header={bankState.header}
                            activeTabId={activeTabId}
                            onTabChange={setActiveTabId}
                        />
                        <div id="bank-items-section">
                            {visibleItems.map((item) => (
                                <BankItem key={item.name} item={item} />
                            ))}
                        </div>
                    </div>
                </div>
                {error && <p className="bank-status bank-error">{error}</p>}
                {lastSyncedAt && (
                    <p className="bank-status">
                        Last synced: {lastSyncedAt.toLocaleString()}
                    </p>
                )}
            </div>
            <Footer />
        </>
    );
}
