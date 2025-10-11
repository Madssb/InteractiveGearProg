import retirement from 'data/retirement.json';
import React, { useState } from 'react';
import { NodeGroup } from "./Chart.jsx";
function RetirementItems(){

    // context menu
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

    // contextmenu invisibility. 
    const [nodeVisibilities, setNodeVisibilities] = useState({})
    
    // hides nodes on hide button click in contextmenu
    function handleHideClick(entity){
        setNodeVisibilities(prev => ({
            ...prev,
            [entity]: "invisible"
        }))
    }

    function handleShowClick(){
        setNodeVisibilities({})
    }


    // turn nodes green on click
    const [nodeStates, setNodeStates] = useState({})
    function handleNodeClick(entity) {
        setNodeStates(prev => ({
            ...prev,
            [entity]: prev[entity] === "complete" ? "incomplete" : "complete"
        }))
    }

    function handleSkipClick(entity) {
        setNodeStates(prev => ({
            ...prev,
            [entity]: prev[entity] === "skipped" ? "incomplete" : "skipped"
        }))
    }



    // menu close
    function handleCloseMenu() {
        setMenu({ ...menu, visible: false });
    }
    // Close context menu when clicking anywhere outside of it
    React.useEffect(() => {
    function handleClickOutside() {
        setMenu(prev => (prev.visible ? { ...prev, visible: false } : prev));
    }
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
    }, []);

    // prevent dragging


    // Load saved states on mount
    React.useEffect(() => {
    try {
        const saved = localStorage.getItem("retirementNodeStates");
        if (saved) {
            const parsed = JSON.parse(saved);
            if (typeof parsed === "object" && parsed !== null) {
                setNodeStates(parsed);
            }
        }
    } catch (err) {
        console.error("Failed to parse saved retirementNodeStates", err);
    }
    }, []);

    // Save every time nodeStates changes
    React.useEffect(() => {
        if (Object.keys(nodeStates).length > 0) {
            localStorage.setItem("retirementNodeStates", JSON.stringify(nodeStates));
        }
    }, [nodeStates]);

    // Load saved nodeVisibilities on mount
    React.useEffect(() => {
        try {
            const savedVisibilities = localStorage.getItem("retirementNodeVisibilities");
            if (savedVisibilities) {
                const parsedVisibilities = JSON.parse(savedVisibilities);
                if (typeof parsedVisibilities === "object" && parsedVisibilities !== null) {
                    setNodeVisibilities(parsedVisibilities)
                }
            }
        } catch (err) {
            console.error("Failed to parse saved nodeVisibilities")
        }
    }, [])

    // save every time nodeVisibilities changes
    React.useEffect(() => {
        if (Object.keys(nodeVisibilities).length > 0) {
            localStorage.setItem("retirementNodeVisibilities", JSON.stringify(nodeVisibilities));
        }
    }, [nodeVisibilities]);
    
    let NodeGroups = Object.values(retirement);
    return (
        <>
        <div
            className='chart'
            style={{ paddingTop: "40px" }}
        >
            {
                NodeGroups.map(
                    (nodeGroup) => (
                        <>
                            <NodeGroup
                                key={nodeGroup}
                                entities={nodeGroup}
                                onContextMenu={handleNodeContextMenu}
                                onTouchStart={handleNodeTouchStart}
                                onTouchEnd={handleNodeTouchEnd}
                                onClick={handleNodeClick}
                                nodeStates={nodeStates}
                                nodeVisibilities={nodeVisibilities}
                            />
                        </>
                    )
                )
            }
        </div>
        </>
    )
}
export default RetirementItems