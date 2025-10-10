import items from 'data/generated/items.json';
import sequence from 'data/sequence.json';
import React, { useState } from 'react';
import ContextMenu from './ContextMenu';
/**
 * Sanitizes a string to create a safe HTML element ID.
 */
function sanitizeId(name) {
    return name.replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').toLowerCase();
}

const pat = /\d+ (\w+)/;

function handleLevels(input) {
  const match = input.match(pat);
  if (match) {
    return match[1];
  }
  return input;
}


/**
 * Renders a node with entity, behavior dependent on if type is skill or non-skill.
 * 
 */
function Node({ entity, onContextMenu, onTouchStart, onTouchEnd, onClick, state }){
    // "86 ranged" is invalid key, "ranged" is valid.
    let itemData = items[handleLevels(entity)];
    
    if (!itemData) {
        console.warn(`Missing data for item: ${entity}`);
        return null;
    }

    let imgUrl =  itemData.imgUrl;
    let wikiUrl = itemData.wikiUrl;
    let id = sanitizeId(entity)
    let type = itemData.type;

    if (type == "skill"){
        let lvlNum = entity.split(" ")[0];
        return (
            <>
            <div
                className={`node ${state} ${type}`}
                title={entity}
                id={sanitizeId(entity)}
                data-wiki-url={wikiUrl}
                aria-label={entity}
                onContextMenu={(e) => onContextMenu(e, entity)}
                onTouchStart={(e) => onTouchStart(e, entity)}
                onTouchEnd={onTouchEnd}
                onClick={() => onClick(entity)}
            >
                <div className='skill'>
                    <img 
                        src={imgUrl}
                        alt=""
                        draggable="false"
                    />
                    <span>{lvlNum}</span>
                </div>
            </div>
            </>
        )
    }
    return (
        <>
        <div
            className={`node ${state} ${type}`}
            title={entity}
            id={id}
            data-wiki-url={wikiUrl}
            onContextMenu={(e) => onContextMenu(e, entity)}
            onTouchStart={(e) => onTouchStart(e, entity)}
            onTouchEnd={onTouchEnd}
            onClick={() => onClick(entity)}
        >
            <img 
                src={imgUrl}
                alt={entity}
                draggable="false"
            />
        </div>
        </>
    )
}

/**
 * Renders a group of nodes
 * 
 */
function NodeGroup({ entities, onContextMenu, onTouchStart, onTouchEnd, onClick, nodeStates }) {
    return (
    <div className="node-group">
      {
        entities.map(entity => (
            <Node
                key={entity}
                entity={entity}
                onContextMenu={onContextMenu}
                onTouchStart={onTouchStart}
                onTouchEnd={onTouchEnd}
                onClick={onClick}
                state={nodeStates[entity] || "incomplete"}
            />
        ))
      }
    </div>
  );
}


// long touch may not be implemented yet

/**
 * Renders a chart composed of grouped nodes.
 * Handles context menu logic and node state (complete, skipped, etc.).
 */
function Chart(){

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
        const saved = localStorage.getItem("nodeStates");
        if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed === "object" && parsed !== null) {
            setNodeStates(parsed);
        }
        }
    } catch (err) {
        console.error("Failed to parse saved nodeStates", err);
    }
    }, []);

    // Save every time nodeStates changes
    React.useEffect(() => {
    if (Object.keys(nodeStates).length > 0) {
        localStorage.setItem("nodeStates", JSON.stringify(nodeStates));
    }
    }, [nodeStates]);

    let nodegroups = Object.values(sequence);
    return (
        <>
            <div className="chart">
                {
                    nodegroups.map(
                        (group, i) => (
                            <React.Fragment key={i}>
                               <NodeGroup
                                    key={group}
                                    entities={group}
                                    onContextMenu={handleNodeContextMenu}
                                    onTouchStart={handleNodeTouchStart}
                                    onTouchEnd={handleNodeTouchEnd}
                                    onClick={handleNodeClick}
                                    nodeStates={nodeStates}
                                />
                                {i < nodegroups.length - 1 && (
                                    <div className='arrow'>→</div>
                                )}
                            </React.Fragment>
                        )
                    )
                }
            </div>
            {menu.visible && (
            <ContextMenu
                x={menu.x}
                y={menu.y}
                entity={menu.entity}
                wikiUrl={items[handleLevels(menu.entity)]?.wikiUrl}
                onClose={handleCloseMenu}
                onSkip={handleSkipClick}
            />
            )}
        </>
    )
}

export default Chart