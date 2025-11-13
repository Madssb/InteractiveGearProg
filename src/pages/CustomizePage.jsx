import Chart from "@/components/Chart.jsx";
import ContextMenu from '@/components/ContextMenu.jsx';
import SequenceForm from '@/components/SequenceForm';
import ShowButton from '@/components/ShowButton.jsx';
import Footer from '@/components/static/Footer.jsx';
import React, { useState } from 'react';



import { useLocalStorageSet, useLocalStorageState } from '@/utils/useLocalStorageState';
// needs a component that represents a sequence input submission htmlform
// needs function that upon submission of the input sequence, makes an api request and gets an items output



// submission happens. inputSequenceState updated with value input.



export default function CustomizePage(){
    
    const [inputSequenceState, setInputSequenceState] = useLocalStorageState('inputSequenceState', false);
    const [outputItemsState, setOutputItemsState] = useLocalStorageState('outputItemsState', false);
    const [nodesCompleteState, setNodesCompleteState] = useLocalStorageSet('nodesCompleteState', new Set());


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

    React.useEffect(() => {
        function handleClickOutside() {
            setMenu(prev => (prev.visible ? { ...prev, visible: false } : prev));
        }
        document.addEventListener("click", handleClickOutside);
        return () => document.removeEventListener("click", handleClickOutside);
    }, []);

    return (
        <>
        <div>
            <h1>Custom Chart</h1>
             <span className="subtitle">Made by Ladlor</span>
        </div>
        <ShowButton
            onShow={handleInputClick}
            buttonText={"Show input"}
        />
        {showInput && (
            <SequenceForm
                inputSequenceState={inputSequenceState}
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
        />
        )}
        <Footer />
        </>
    )
}
// hide argument is missing. governs categorywide hiding
// nodesHiddenState missing. governs items hidden or no
// 
