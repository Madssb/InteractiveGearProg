import Chart from "@/components/Chart.jsx";
import ContextMenu from '@/components/ContextMenu.jsx';
import SequenceForm from '@/components/SequenceForm';
import Footer from '@/components/static/Footer.jsx';
import { useLocalStorageSet, useLocalStorageState } from '@/utils/useLocalStorageState';
import React, { useState } from 'react';
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

        const shareUrl = `${base}#/customize?token=${token}`;
        navigator.clipboard.writeText(shareUrl);

    } catch (err) {
        console.error(err);
    }
}


export default function CustomizePage(){    
    const [inputSequenceState, setInputSequenceState] = useLocalStorageState('inputSequenceState', false);
    const [outputItemsState, setOutputItemsState] = useLocalStorageState('outputItemsState', false);
    const [nodesCompleteState, setNodesCompleteState] = useLocalStorageSet('nodesCompleteState', new Set());

    // initialize from Share-URL
    const location = useLocation();


    React.useEffect(() => {
        const params = new URLSearchParams(location.search);
        const token = params.get("token");
        if (token) fetchShare(token);
    }, [location.search]);

    async function fetchShare(token) {
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
    }

    function extractSequence() {
        if (!inputSequenceState) return;
        const json = JSON.stringify(inputSequenceState);
        navigator.clipboard.writeText(json);
    }


    const [showInput, setShowInput] = useState(false);
    function handleInputClick() {
        setShowInput(!showInput)
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
    const panelStyle = {"justifyContent": "center", "display":"flex", "alignItems": "center"}
    const buttonStyle = {"backgroundColor": "gray"}
    const topStyle = {"justifyContent": "space-between", "display":"flex", "alignItems": "center"}

    const actions = [
        { handler: handleInputClick, label: "Show input" },
        { 
        handler: () => postShare(inputSequenceState, outputItemsState), 
        label: "Share" 
        },
        { handler: extractSequence,  label: "Extract" }
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
                <h1>Custom Chart</h1>
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
        <Footer />
        </>
    )
}
