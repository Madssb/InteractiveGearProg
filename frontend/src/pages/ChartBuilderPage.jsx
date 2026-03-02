import Chart from "@/components/Chart.jsx";
import ContextMenu from '@/components/ContextMenu.jsx';
import SequenceForm from '@/components/SequenceForm';
import Footer from '@/components/static/Footer.jsx';
import removeStarredItems from '@/utils/removeStarredItems.js';
import { handleLevels } from '@/utils/textSanitizers';
import { useLocalStorageSet, useLocalStorageState } from '@/utils/useLocalStorageState';
import sequence from '@data/logic/sequence.json';
import React, { useCallback, useState } from 'react';
import { useLocation } from "react-router";

async function postShare(inputSequenceState, outputItemsState) {
    if (!inputSequenceState || !outputItemsState) return;

    const url = "https://api.ladlorchart.com/share/";
    // const url = "http://127.0.0.1:8000/share/" // Localhost testing
    const base = window.location.origin + window.location.pathname;

    const payload = {
        sequence: inputSequenceState,   // nested list
        items: outputItemsState         // dict of ItemInfo
    };

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Response status: ${response.status}`);

        const token = await response.json();   // or .text() if backend returns plain string

        // Use chartbuilder as canonical link; /customize is kept as alias.
        const shareUrl = `${base}#/chartbuilder?token=${token}`;
        navigator.clipboard.writeText(shareUrl);

    } catch (err) {
        console.error(err);
    }
}

async function fetchMissingItems(sequenceArray, outputItemsState, setOutputItemsState) {
    const url = "https://api.ladlorchart.com/sequence/"; // Remote
    // const url = "http://127.0.0.1:8000/sequence/" // Localhost testing
    const flat = sequenceArray.flat().map(handleLevels);
    const keySet = new Set(Object.keys(outputItemsState || {}));
    const payload = [...new Set(flat.filter(item => !keySet.has(item)))];
    if (payload.length === 0) return;

    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ sequence: payload })
    });

    if (!response.ok) throw new Error(`Response status: ${response.status}`);
    const result = await response.json();
    const items = result.items || {};
    setOutputItemsState(prev => ({ ...prev, ...items }));
}


export default function ChartBuilderPage() {
    const [inputSequenceState, setInputSequenceState] = useLocalStorageState('inputSequenceState', false);
    const [outputItemsState, setOutputItemsState] = useLocalStorageState('outputItemsState', false);
    const [nodesCompleteState, setNodesCompleteState] = useLocalStorageSet('nodesCompleteState', new Set());
    const [loadingLadlorChart, setLoadingLadlorChart] = useState(false);
    const [loadError, setLoadError] = useState("");

    // initialize from Share-URL
    const location = useLocation();


    const fetchShare = useCallback(async (token) => {
        try {
            const response = await fetch(`https://api.ladlorchart.com/share/?token=${token}`);
            // const response = await fetch(`http://127.0.0.1:8000/share/?token=${token}`);
            if (!response.ok) throw new Error(`status ${response.status}`);

            const share = await response.json();

            // share = { sequence: [...], items: {...} }
            setInputSequenceState(share.sequence);
            setOutputItemsState(share.items);
        } catch (err) {
            console.error(err);
        }
    }, [setInputSequenceState, setOutputItemsState]);

    React.useEffect(() => {
        const params = new URLSearchParams(location.search);
        const token = params.get("token");
        if (token) fetchShare(token);
    }, [location.search, fetchShare]);

    function extractSequence() {
        if (!inputSequenceState) return;
        const json = JSON.stringify(inputSequenceState);
        navigator.clipboard.writeText(json);
    }


    const [showInput, setShowInput] = useState(false);
    function handleInputClick() {
        setShowInput(!showInput)
    }
    async function handleLoadLadlorChart() {
        setLoadError("");
        const hasExisting = Boolean(inputSequenceState && inputSequenceState.length);
        if (hasExisting) {
            const shouldReplace = window.confirm("Replace your current chart with Ladlor's chart?");
            if (!shouldReplace) return;
        }

        const ladlorSequence = removeStarredItems(sequence);
        setInputSequenceState(ladlorSequence);
        try {
            setLoadingLadlorChart(true);
            await fetchMissingItems(ladlorSequence, outputItemsState, setOutputItemsState);
        } catch (error) {
            console.error(error);
            setLoadError("Could not load Ladlor chart item metadata. Please try again.");
        } finally {
            setLoadingLadlorChart(false);
        }
    }

    function handleNodeClick(entity) {
        setNodesCompleteState(prev => {
            const next = new Set(prev);
            if (next.has(entity)) next.delete(entity);
            else next.add(entity);
            return next;
        });
    }

    // Context menu
    const [menu, setMenu] = useState({
        visible: false,
        x: 0,
        y: 0,
        entity: null,
    });
    function handleNodeContextMenu(e, entity) {
        e.preventDefault();
        const touch = e.touches?.[0] || e.changedTouches?.[0];
        const x = touch?.pageX ?? e.pageX;
        const y = touch?.pageY ?? e.pageY;
        setMenu({
            visible: true,
            x,
            y,
            entity,
        });
    }

    // long press behaves like right click
    function handleNodeTouchStart(e, entity) {
        e.persist?.(); // keep event for later
        const timeoutId = setTimeout(() => {
            handleNodeContextMenu(e, entity); // trigger context menu
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

    function handleDelete(entity) {
        setInputSequenceState(seq =>
            seq
                .map(group => group.filter(item => item !== entity))
                .filter(group => group.length > 0)
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
            handler: () => postShare(inputSequenceState, outputItemsState),
            label: "Share"
        },
        { handler: extractSequence, label: "Extract" },
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
                    outputItemsState={outputItemsState}
                    setInputSequenceState={setInputSequenceState}
                    setOutputItemsState={setOutputItemsState}
                    initialSequence={inputSequenceState}
                />
            )}
            {inputSequenceState && outputItemsState && (
                <Chart
                    nodeGroups={inputSequenceState}
                    items={outputItemsState}
                    nodesCompleteState={nodesCompleteState}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    arrows={true}
                />
            )}
            {menu.visible && (
                <ContextMenu
                    x={menu.x}
                    y={menu.y}
                    entity={menu.entity}
                    onClose={handleCloseMenu}
                    onDelete={handleDelete}
                    items={outputItemsState}
                />
            )}
            {loadError && <p style={{ color: "crimson" }}>{loadError}</p>}
            <Footer showImageAttribution={true} />
        </>
    )
}
