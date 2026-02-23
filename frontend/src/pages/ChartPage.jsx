import Chart from "@/components/Chart.jsx";
import ConfigMenu from "@/components/ConfigMenu";
import ContextMenu from '@/components/ContextMenu.jsx';
import Acknowledgements from '@/components/static/Acknowledgements.jsx';
import FAQSection from '@/components/static/FAQSection.jsx';
import Footer from '@/components/static/Footer.jsx';
import '@/styles/ChartPage.css';
import migrateLegacySharedNodeStates from '@/utils/migrateState';
import removeStarredItems from '@/utils/removeStarredItems.js';
import updateSequenceLanceRule from '@/utils/sequenceRules.js';
import { useLocalStorageSet, useLocalStorageState } from '@/utils/useLocalStorageState';
import items from '@data/generated/items.json';
import sequenceBareBones from '@data/generated/sequence-bare-bones.json';
import retirement from '@data/logic/retirement.json';
import sequence from '@data/logic/sequence.json';
import React, { useState } from 'react';


export default function ChartPage(){
    // chart rendering
    const [showRetirement, setShowRetirement] = useLocalStorageState('showRetirement', false);
    const [showBareBones, setShowBareBones] = useLocalStorageState('showBareBones', false);
    const [showOptions, setShowOptions] = useState(false);

    const [nodesHiddenState, setNodesHiddenState] = useLocalStorageSet('nodesHiddenState', new Set());
    const [nodesCompleteState, setNodesCompleteState] = useLocalStorageSet('nodesCompleteState', new Set());
    const [hide, setHide] = useLocalStorageState('hide', {
        item: false,
        prayer: false,
        construction: false,
        slayer: false,
        spell: false,
        skill: false,
    });
    function handleHideClick(entity){
        setNodesHiddenState(prev => {
            const next = new Set(prev);
            if (next.has(entity)) next.delete(entity);
            else next.add(entity);
            return next;
        });
    }
    function handleShowClick(){
        setNodesHiddenState(new Set());
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

    let nodeGroups = Object.values(removeStarredItems(sequence));
    let nodeGroupsBareBones = Object.values(removeStarredItems(sequenceBareBones));
    let nodeGroupsRetirement = Object.values(retirement);
    const style = {"justifyContent": "space-between", "display":"flex", "alignItems": "center"}
    
    // if scythe is missing, lance is worth getting at the same step where ferocious gloves lives.
    const [nodeGroupsState, setNodeGroupsState] = useState(nodeGroups);
    const [nodeGroupsBareBonesState, setNodeGroupsBareBonesState] = useState(nodeGroupsBareBones)
    React.useEffect(() => {
        setNodeGroupsState(prev => updateSequenceLanceRule(nodesHiddenState, prev));
        setNodeGroupsBareBonesState(prev => updateSequenceLanceRule(nodesHiddenState, prev));
    }, [nodesHiddenState])

    
    migrateLegacySharedNodeStates(setNodesCompleteState);
    return (
        <>
            
            <div style={style}>
                    <div />
                    <div>
                        <h1>Interactive Ironman Progression Chart</h1>
                        <span className="subtitle">Curated by the Ironscape community — made by Ladlor</span>
                    </div>
                    <button
                        className={showOptions ? "active": ""}
                        onClick={() => setShowOptions(!showOptions)}
                        id="options-button"
                        aria-label="Show settings"
                    >
                        <img src="https://oldschool.runescape.wiki/images/Settings.png"/>
                    </button>
            </div>
            {showOptions && (
                <ConfigMenu
                    showRetirement={showRetirement}
                    setShowRetirement={setShowRetirement}
                    showBareBones={showBareBones}
                    setShowBareBones={setShowBareBones}
                    hide={hide}
                    setHide={setHide}
                />
            )}
            {showBareBones && (
                <Chart
                    nodeGroups={nodeGroupsBareBonesState}
                    items={items}
                    hide={hide}
                    nodesHiddenState={nodesHiddenState}
                    nodesCompleteState={nodesCompleteState}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    arrows={true}
                />
            )}
            {!showBareBones && (
                <Chart
                    nodeGroups={nodeGroupsState}
                    items={items}
                    hide={hide}
                    nodesHiddenState={nodesHiddenState}
                    nodesCompleteState={nodesCompleteState}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    arrows={true}
                />
            )}
            {showRetirement && (
                <Chart
                    nodeGroups={nodeGroupsRetirement}
                    items={items}
                    hide={hide}
                    nodesHiddenState={nodesHiddenState}
                    nodesCompleteState={nodesCompleteState}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    arrows={false}
                />
            )}
            {nodesHiddenState.size > 0 && (
            <button
                id="show-button"
                onClick={handleShowClick}
            >
                Show hidden items
            </button>
            )}   
            {menu.visible && (
            <ContextMenu
                x={menu.x}
                y={menu.y}
                entity={menu.entity}
                onClose={handleCloseMenu}
                onHide={handleHideClick}
                items={items}
            />
            )}
            <Acknowledgements />
            <FAQSection />
            <Footer />
        </>
    )
}
