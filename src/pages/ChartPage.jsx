import Chart from "@/components/Chart.jsx";
import ContextMenu from '@/components/ContextMenu.jsx';
import ShowButton from '@/components/ShowButton.jsx';
import Acknowledgements from '@/components/static/Acknowledgements.jsx';
import FAQSection from '@/components/static/FAQSection.jsx';
import Footer from '@/components/static/Footer.jsx';
import ToggleButton from '@/components/ToggleButton.jsx';
import TogglePanel from '@/components/TogglePanel.jsx';
import { useLocalStorageSet, useLocalStorageState } from '@/utils/useLocalStorageState';
import sequenceBareBones from '@data/generated/sequence-bare-bones.json';
import retirement from '@data/retirement.json';
import sequence from '@data/sequence.json';
import React, { useState } from 'react';



export default function ChartPage(){
    // chart rendering
    const [showRetirement, setShowRetirement] = useLocalStorageState(false);
    const [showBareBones, setShowBareBones] = useLocalStorageState(false);

    const [nodesHiddenState, setNodesHiddenState] = useLocalStorageSet('nodesHiddenState', new Set());
    const [nodesCompleteState, setNodesCompleteState] = useLocalStorageSet('nodesCompleteState', new Set());
 
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

    const [hide, setHide] = useState({
        item: false,
        prayer: false,
        construction: false,
        slayer: false,
        spell: false,
        skill: false,
    });



    let nodeGroups = Object.values(sequence);
    let nodeGroupsBareBones = Object.values(sequenceBareBones);
    let nodeGroupsRetirement = Object.values(retirement);

    return (
        <>
            <h1>Interactive Ironman Progression Chart</h1>
            <span className="subtitle">Curated by the Ironscape community — made by Ladlor</span>
            <TogglePanel>
                <ToggleButton
                    id="retirement-toggle"
                    value={showRetirement}
                    onToggle={setShowRetirement}
                    label={"Re"}
                    icon={"https://oldschool.runescape.wiki/images/Collection_log.png"}
                />
                <ToggleButton
                    id="bare-bones-toggle"
                    value={showBareBones}
                    onToggle={setShowBareBones}
                    icon={"https://oldschool.runescape.wiki/images/Bones.png"}
                    label={"Ba"}
                />
                <ToggleButton
                    id="hide-skill"
                    value={hide.skill}
                    onToggle={v => setHide(prev => ({ ...prev, skill: v }))}
                    label="Skill"
                    icon={"https://oldschool.runescape.wiki/images/Stats_icon.png"}
                />

                <ToggleButton
                    id="hide-construction"
                    value={hide.construction}
                    onToggle={v => setHide(prev => ({ ...prev, construction: v }))}
                    label="Construction"
                    icon={"https://oldschool.runescape.wiki/images/Construction_icon.png"}
                />

                <ToggleButton
                    id="hide-slayer"
                    value={hide.slayer}
                    onToggle={v => setHide(prev => ({ ...prev, slayer: v }))}
                    label="Slayer"
                    icon={"https://oldschool.runescape.wiki/images/Slayer_icon.png"}
                />
            </TogglePanel>
            {showBareBones && (
                <Chart
                    nodeGroups={nodeGroupsBareBones} 
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
                    nodeGroups={nodeGroups} 
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
            <ShowButton
                onShow={handleShowClick}
            />
            )}   
            {menu.visible && (
            <ContextMenu
                x={menu.x}
                y={menu.y}
                entity={menu.entity}
                onClose={handleCloseMenu}
                onHide={handleHideClick}
            />
            )}
            <Acknowledgements />
            <FAQSection />
            <Footer />
        </>
    )
}
