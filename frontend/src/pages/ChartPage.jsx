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
import milestoneMetadata from '@data/generated/milestone-metadata.json';
import milestoneSequenceBarebonesRaw from '@data/generated/milestone-sequence-barebones.json';
import milestoneSequenceRetirementRaw from '@data/logic/milestone-sequence-retirement.json';
import milestoneSequenceMainRaw from '@data/logic/milestone-sequence-main.json';
import React, { useState } from 'react';


export default function ChartPage(){

    
    const [showRetirement, setShowRetirement] = useLocalStorageState('showRetirement', false);
    const [showBareBones, setShowBareBones] = useLocalStorageState('showBareBones', false);
    const [showOptions, setShowOptions] = useState(false);

    const [milestonesHidden, setMilestonesHidden] = useLocalStorageSet('milestonesHidden', new Set(), ['nodesHiddenState']);
    const [milestonesComplete, setMilestonesComplete] = useLocalStorageSet('milestonesComplete', new Set(), ['nodesCompleteState']);
    const [hide, setHide] = useLocalStorageState('hide', {
        item: false,
        prayer: false,
        construction: false,
        slayer: false,
        spell: false,
        skill: false,
    });
    function handleHideClick(milestone){
        setMilestonesHidden(prev => {
            const next = new Set(prev);
            if (next.has(milestone)) next.delete(milestone);
            else next.add(milestone);
            return next;
        });
    }
    function handleShowClick(){
        setMilestonesHidden(new Set());
    }
    function handleNodeClick(milestone) {
        setMilestonesComplete(prev => {
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

    React.useEffect(() => {
        function handleClickOutside() {
            setMenu(prev => (prev.visible ? { ...prev, visible: false } : prev));
        }
        document.addEventListener("click", handleClickOutside);
        return () => document.removeEventListener("click", handleClickOutside);
    }, []);

    let milestoneSequenceMain = removeStarredItems(milestoneSequenceMainRaw);
    let milestoneSequenceBarebones = removeStarredItems(milestoneSequenceBarebonesRaw);
    let milestoneSequenceRetirement = milestoneSequenceRetirementRaw;
    
    
    // if scythe is missing, lance is worth getting at the same step where ferocious gloves lives.
    const [milestoneSequenceMainFiltered, setMilestoneSequenceMainFiltered] = useState(milestoneSequenceMain);
    const [milestoneSequenceBarebonesFiltered, setMilestoneSequenceBarebonesFiltered] = useState(milestoneSequenceBarebones)
    React.useEffect(() => {
        setMilestoneSequenceMainFiltered(prev => updateSequenceLanceRule(milestonesHidden, prev));
        setMilestoneSequenceBarebonesFiltered(prev => updateSequenceLanceRule(milestonesHidden, prev));
    }, [milestonesHidden])
    
    React.useEffect(() => {
        migrateLegacySharedNodeStates(setMilestonesComplete);
    }, [setMilestonesComplete]);
    
    const style = {"justifyContent": "space-between", "display":"flex", "alignItems": "center"}
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
                    milestoneSequence={milestoneSequenceBarebonesFiltered}
                    milestoneMetadata={milestoneMetadata}
                    milestonesComplete={milestonesComplete}
                    milestonesHidden={milestonesHidden}
                    hide={hide}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    arrows={true}
                />
            )}
            {!showBareBones && (
                <Chart
                    milestoneSequence={milestoneSequenceMainFiltered}
                    milestoneMetadata={milestoneMetadata}
                    milestonesComplete={milestonesComplete}
                    milestonesHidden={milestonesHidden}
                    hide={hide}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    arrows={true}
                />
            )}
            {showRetirement && (
                <Chart
                    milestoneSequence={milestoneSequenceRetirement}
                    milestoneMetadata={milestoneMetadata}
                    milestonesComplete={milestonesComplete}
                    milestonesHidden={milestonesHidden}
                    hide={hide}
                    handleNodeContextMenu={handleNodeContextMenu}
                    handleNodeTouchStart={handleNodeTouchStart}
                    handleNodeTouchEnd={handleNodeTouchEnd}
                    handleNodeClick={handleNodeClick}
                    arrows={false}
                />
            )}
            {milestonesHidden.size > 0 && (
            <button
                id="show-button"
                onClick={handleShowClick}
            >
                Show hidden items
            </button>
            )}   
            {menu.visible && (
            <ContextMenu
            milestone={menu.milestone}
            milestoneMetadata={milestoneMetadata}
            onClose={handleCloseMenu}
            onHide={handleHideClick}
            x={menu.x}
            y={menu.y}
            />
            )}
            <Acknowledgements />
            <FAQSection />
            <Footer showImageAttribution={true} />
        </>
    )
}
