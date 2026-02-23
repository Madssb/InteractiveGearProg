import { handleLevels, sanitizeId } from '@/utils/textSanitizers';
import React from 'react';

/**
 * Renders a node with entity, behavior dependent on if type is skill or non-skill.
 * 
 */
function Node({
        entity,
        items,
        onContextMenu,
        onTouchStart,
        onTouchEnd,
        onClick,
        nodeCompleteState, 
        nodeHiddenState
    }){
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
                className={`node ${nodeCompleteState && "complete"}`}
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
            className={`node ${nodeCompleteState && "complete"} ${nodeHiddenState && "hidden" } ${type}`}
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
function NodeGroup({
        entities, 
        items,
        onContextMenu, 
        onTouchStart, 
        onTouchEnd, 
        onClick, 
        nodesCompleteState, 
        nodesHiddenState, 
        hide
    }) {
    // entities in nodesHiddenState omitted from rendering
    let final;
    if (hide && nodesHiddenState){
        const entitiesNotHidden = entities.filter(e => {
            if (nodesHiddenState.has(e)){
                return false;
            } else {
                return true;
            }
        })
        const entitiesNotHiddenNotFiltered = entitiesNotHidden.filter(e => {
            const key = handleLevels(e);
            const itemData = items[key];
            if (!itemData) {
                console.warn(`Missing data for entity: ${e}`);
                return false;
            }
            return !hide[itemData.type];
        });
        final = entitiesNotHiddenNotFiltered
    } else {
        final = entities;
    }
    return (
    <div className={"node-group"}>
      {
        final.map(entity => (
            <Node
                key={entity}
                items={items}
                entity={entity}
                onContextMenu={onContextMenu}
                onTouchStart={onTouchStart}
                onTouchEnd={onTouchEnd}
                onClick={onClick}
                nodeCompleteState={nodesCompleteState?.has(entity)}
                nodeHiddenState={nodesHiddenState?.has(entity)}

            />
        ))
      }
    </div>
  );
}

/**
 * Renders a chart composed of grouped nodes.
 * Handles context menu logic and node state (complete, skipped, etc.).
*/
export default function Chart( {
        nodeGroups,
        items,
        hide,
        nodesHiddenState,
        nodesCompleteState,
        handleNodeContextMenu,
        handleNodeTouchStart,
        handleNodeTouchEnd,
        handleNodeClick,
        arrows
    } ){
    let visibleGroups;
    if (hide){
        visibleGroups = nodeGroups.filter(group =>
        group.some(entity => {
            if (nodesHiddenState.has(entity)) return false;
            const key = handleLevels(entity);
            const itemData = items[key];
            if (!itemData) return false;
            return !hide[itemData.type];
        })
        );
    } else {
        visibleGroups = nodeGroups;
    }
    return (
        <div
        className={"chart"}
        >
            {
                visibleGroups.map(
                    (nodeGroup, i) => (
                        <React.Fragment key={i}>
                            <NodeGroup
                                key={nodeGroup}
                                entities={nodeGroup}
                                items={items}
                                onContextMenu={handleNodeContextMenu}
                                onTouchStart={handleNodeTouchStart}
                                onTouchEnd={handleNodeTouchEnd}
                                onClick={handleNodeClick}
                                nodesCompleteState={nodesCompleteState}
                                nodesHiddenState={nodesHiddenState}
                                hide={hide}
                            />
                            {arrows && i < nodeGroups.length - 1 && (
                                <div className='arrow'>→</div>
                            )}
                        </React.Fragment>
                    )
                )
            }
        </div>
    )
}
