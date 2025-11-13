import Chart from "@/components/Chart.jsx";
import ContextMenu from '@/components/ContextMenu.jsx';
import SequenceForm from '@/components/SequenceForm';
import Footer from '@/components/static/Footer.jsx';
import { useLocalStorageSet, useLocalStorageState } from '@/utils/useLocalStorageState';
import LZString from "lz-string";
import React, { useState } from 'react';
import { useLocation } from "react-router";


export default function CustomizePage(){    
    const [inputSequenceState, setInputSequenceState] = useLocalStorageState('inputSequenceState', false);
    const [outputItemsState, setOutputItemsState] = useLocalStorageState('outputItemsState', false);
    const [nodesCompleteState, setNodesCompleteState] = useLocalStorageSet('nodesCompleteState', new Set());

    // initialize from Share-URL
    const location = useLocation();

    React.useEffect(() => {
        const param = new URLSearchParams(location.search).get("data");
        if (!param) return;

        const json = LZString.decompressFromEncodedURIComponent(param);
        if (!json) return;

        const parsed = JSON.parse(json);

        if (parsed.seq) setInputSequenceState(parsed.seq);
        if (parsed.items) setOutputItemsState(parsed.items);
    }, [location.search]);

    function makeShareLink() {
        if (!inputSequenceState || !outputItemsState) return;

        const payload = {
            seq: inputSequenceState,
            items: outputItemsState
        };

        const json = JSON.stringify(payload);
        const encoded = LZString.compressToEncodedURIComponent(json);
        const base = window.location.origin + window.location.pathname;
        const shareUrl = `${base}#/customize?data=${encoded}`;
        navigator.clipboard.writeText(shareUrl);
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
        { handler: makeShareLink,    label: "Share" },
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
