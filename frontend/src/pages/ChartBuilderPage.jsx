import Chart from "@/components/Chart";
import ContextMenu from '@/components/ContextMenu.jsx';
import SequenceForm from '@/components/SequenceForm';
import Footer from '@/components/static/Footer.jsx';
import { apiUrl } from '@/utils/apiConfig';
import removeStarredItems from '@/utils/removeStarredItems.js';
import { handleLevels } from '@/utils/textSanitizers';
import { useLocalStorageSet, useLocalStorageState } from '@/utils/useLocalStorageState';
import milestoneSequenceMainRaw from '@data/logic/milestone-sequence-main.json';
import React, { useState } from 'react';
import { useLocation } from "react-router";

/*
Instantiate chartbuilder-share record.
*/
// stores milestoneSequence in chartbuilder-share record
async function postShare(milestoneSequence) {
    
    if (!milestoneSequence) return;

    const url = apiUrl("/share/");
    const base = window.location.origin + window.location.pathname;

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(milestoneSequence)
        });

        if (!response.ok) throw new Error(`Response status: ${response.status}`);

        const token = await response.json();

        // Use chartbuilder as canonical link; /customize is kept as alias.
        const shareUrl = `${base}#/chartbuilder?token=${token}`;
        navigator.clipboard.writeText(shareUrl);

    } catch (err) {
        console.error(err);
    }
}

// fetches milestoneSequence, updates milestoneMetadata as needed  
async function getShare(token, setMilestoneSequence, milestoneMetadata, setMilestoneMetadata) {
    if (!token) return;
    const url = apiUrl(`/share/?token=${token}`);

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Response status: ${response.status}`);
        const milestoneSequence = await response.json();
        setMilestoneSequence(milestoneSequence);
        await fetchMissingMilestoneMetadata(milestoneSequence, milestoneMetadata, setMilestoneMetadata);
    } catch (err) {
            console.error(err);
    }
}

async function fetchMissingMilestoneMetadata(milestoneSequence, milestoneMetadata, setMilestoneMetadata) {
    const url = apiUrl("/fetch-milestone-metadata/");
    const milestoneSequenceProcessed = (milestoneSequence || [])
        .flat(Infinity)
        .filter(milestone => typeof milestone === "string")
        .map(handleLevels);
    const milestonesInMetadata = new Set(Object.keys(milestoneMetadata || {}));
    const milestonesToFetch = [...new Set(milestoneSequenceProcessed.filter(milestone => !milestonesInMetadata.has(milestone)))];
    
    if (milestonesToFetch.length === 0) return;

    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(milestonesToFetch)
    });
    if (!response.ok) throw new Error(`Response status: ${response.status}`);
    const result = await response.json();
    const milestoneMetadataFetched = result.milestoneMetadata || {};
    setMilestoneMetadata(prev => ({ ...prev, ...milestoneMetadataFetched }));
}

function extractSequence(milestoneSequence) {
    if (!milestoneSequence) return;
    const json = JSON.stringify(milestoneSequence);
    navigator.clipboard.writeText(json);
}

export default function ChartBuilderPage() {
    const [milestoneSequenceChartBuilder, setMilestoneSequenceChartBuilder] = useLocalStorageState(
        'milestoneSequenceChartBuilder',
        false,
        ['inputSequenceState']
    );
    const [milestoneMetadata, setMilestoneMetadata] = useLocalStorageState('milestoneMetadata', false);
    const [nodesCompleteState, setNodesCompleteState] = useLocalStorageSet('nodesCompleteState', new Set());
    const [loadingLadlorChart, setLoadingLadlorChart] = useState(false);
    const [loadError, setLoadError] = useState("");

    // initialize from Share-URL
    const location = useLocation();

    React.useEffect(() => {
        const params = new URLSearchParams(location.search);
        const token = params.get("token");
        if (token) {
            getShare(token, setMilestoneSequenceChartBuilder, milestoneMetadata, setMilestoneMetadata);
        }
    }, [location.search, milestoneMetadata, setMilestoneSequenceChartBuilder, setMilestoneMetadata]);


    const [showInput, setShowInput] = useState(false);
    function handleInputClick() {
        setShowInput(!showInput)
    }

    async function handleLoadLadlorChart() {
        setLoadError("");
        const hasExisting = Boolean(milestoneSequenceChartBuilder && milestoneSequenceChartBuilder.length);
        if (hasExisting) {
            const shouldReplace = window.confirm("Replace your current chart with Ladlor's chart?");
            if (!shouldReplace) return;
        }

        const ladlorMilestoneSequence = removeStarredItems(milestoneSequenceMainRaw);
        setMilestoneSequenceChartBuilder(ladlorMilestoneSequence);
        try {
            setLoadingLadlorChart(true);
            await fetchMissingMilestoneMetadata(ladlorMilestoneSequence, milestoneMetadata, setMilestoneMetadata);
        } catch (error) {
            console.error(error);
            setLoadError("Could not load Ladlor chart milestone metadata. Please try again.");
        } finally {
            setLoadingLadlorChart(false);
        }
    }

    function handleNodeClick(milestone) {
        setNodesCompleteState(prev => {
            const next = new Set(prev);
            if (next.has(milestone)) next.delete(milestone);
            else next.add(milestone);
            return next;
        });
    }

    // Context menu
    const [menu, setMenu] = useState({
        visible: false,
        x: 0,
        y: 0,
        milestone: null,
    });
    function handleNodeContextMenu(e, milestone) {
        e.preventDefault();
        const touch = e.touches?.[0] || e.changedTouches?.[0];
        const x = touch?.pageX ?? e.pageX;
        const y = touch?.pageY ?? e.pageY;
        setMenu({
            visible: true,
            x,
            y,
            milestone,
        });
    }

    // long press behaves like right click
    function handleNodeTouchStart(e, milestone) {
        e.persist?.(); // keep event for later
        const timeoutId = setTimeout(() => {
            handleNodeContextMenu(e, milestone); // trigger context menu
        }, 600); // long-press threshold
        e.target.dataset.longPressTimeout = timeoutId;
    }

    function handleNodeTouchEnd(e) {
        const timeoutId = e.target.dataset.longPressTimeout;
        if (timeoutId) clearTimeout(timeoutId);
    }

    function handleCloseMenu() {
        setMenu({ ...menu, visible: false });
    }

    function handleDelete(milestoneToDelete) {
        setMilestoneSequenceChartBuilder(seq =>
            seq
                .map(milestoneGroup => milestoneGroup.filter(milestone => milestone !== milestoneToDelete))
                .filter(milestoneGroup => milestoneGroup.length > 0)
        );
    }

    React.useEffect(() => {
        function handleClickOutside() {
            setMenu(prev => (prev.visible ? { ...prev, visible: false } : prev));
        }
        document.addEventListener("click", handleClickOutside);
        return () => document.removeEventListener("click", handleClickOutside);
    }, []);
    const buttonStyle = { "backgroundColor": "gray" }

    const actions = [
        { handler: handleInputClick, label: "Show input" },
        {
            handler: () => postShare(milestoneSequenceChartBuilder, milestoneMetadata),
            label: "Share"
        },
        { handler: () => extractSequence(milestoneSequenceChartBuilder), label: "Extract" },
        {
            handler: handleLoadLadlorChart,
            label: loadingLadlorChart ? "Loading..." : "Load Main Chart",
            disabled: loadingLadlorChart
        }
    ];
    return (
        <>
            <div id="titleBar" style={{ position: "relative", height: "80px" }}>
                <div style={{
                    position: "absolute",
                    left: "50%",
                    top: "50%",
                    transform: "translate(-50%, -50%)",
                    textAlign: "center"
                }}>
                    <h1>Chart Builder</h1>
                    <span className="subtitle">Made by Ladlor</span>
                </div>
                <div style={{
                    position: "absolute",
                    right: "0",
                    top: "50%",
                    transform: "translateY(-50%)",
                    display: "flex",
                    gap: "8px"
                }}>
                    {actions.map(a => (
                        <button
                            key={a.label}
                            onClick={a.handler}
                            disabled={Boolean(a.disabled)}
                            style={buttonStyle}
                        >
                            {a.label}
                        </button>
                    ))}
                </div>
            </div>

            {showInput && (
                <SequenceForm
                    outputItemsState={milestoneMetadata}
                    setMilestoneSequence={setMilestoneSequenceChartBuilder}
                    setOutputItemsState={setMilestoneMetadata}
                    initialSequence={milestoneSequenceChartBuilder}
                />
            )}
            {milestoneSequenceChartBuilder && milestoneMetadata && (
                <Chart
                    milestoneSequence={milestoneSequenceChartBuilder}
                    milestoneMetadata={milestoneMetadata}
                    milestonesComplete={nodesCompleteState}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    arrows={true}
                />
            )}
            {menu.visible && (
                <ContextMenu
                    milestone={menu.milestone}
                    milestoneMetadata={milestoneMetadata}
                    onClose={handleCloseMenu}
                    onDelete={handleDelete}
                    x={menu.x}
                    y={menu.y}
                />
            )}
            {loadError && <p style={{ color: "crimson" }}>{loadError}</p>}
            <Footer showImageAttribution={true} />
        </>
    )
}
