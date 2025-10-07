import items from 'data/generated/items.json';
import sequence from 'data/sequence.json';
import React, { useState } from 'react';
import ContextMenu from './RightClick';

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

function Node({ entity, onContextMenu }){
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
                className={`node ${type}`}
                title={entity}
                id={sanitizeId(entity)}
                data-wiki-url={wikiUrl}
                aria-label={entity}
                onContextMenu={(e) => onContextMenu(e, entity)}
            >
                <div className='skill'>
                    <img 
                        src={imgUrl}
                        alt=""
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
            className={`node ${type}`}
            title={entity}
            id={id}
            data-wiki-url={wikiUrl}
            onContextMenu={(e) => onContextMenu(e, entity)}
        >
            <img 
                src={imgUrl}
                alt={entity} 
            />
        </div>
        </>
    )
}

function NodeGroup({ entities, onContextMenu }) {
    return (
    <div className="node-group">
      {
        entities.map(entity => (
            <Node key={entity} entity={entity} onContextMenu={onContextMenu}/>
        ))
      }
    </div>
  );
}

function Chart(){
    const [menu, setMenu] = useState({
        visible: false,
        x: 0,
        y: 0,
        entity: null,
    });

    function handleNodeContextMenu(e, entity) {
        console.log(entity)
        console.log(menu)
        e.preventDefault();
        setMenu({
        visible: true,
        x: e.pageX,
        y: e.pageY,
        entity,
        });
    }

    function handleCloseMenu() {
        setMenu({ ...menu, visible: false });
    }

    // Close context menu when clicking anywhere outside of it
    React.useEffect(() => {
    function handleClickOutside(e) {
        setMenu(prev => (prev.visible ? { ...prev, visible: false } : prev));
    }
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
    }, []);

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
                title={menu.entity}
                wikiUrl={items[handleLevels(menu.entity)]?.wikiUrl}
                onClose={handleCloseMenu}
            />
            )}
        </>
    )
}

export default Chart