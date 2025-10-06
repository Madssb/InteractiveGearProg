import items from 'data/generated/items.json';
import sequence from 'data/sequence.json';
import React from 'react';
import 'styles/chart.css';

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


function Node({ entity }){
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
        >
            <img 
                src={imgUrl}
                alt={entity} 
            />
        </div>
        </>
    )
}

function NodeGroup({ entities }) {
    return (
    <div className="node-group">
      {
        entities.map(entity => (
            <Node key={entity} entity={entity}/>
        ))
      }
    </div>
  );
}

function Chart(){
    let nodegroups = Object.values(sequence);
    return (
        <>
            <div className="chart">
                {
                    nodegroups.map(
                        (group, i) => (
                            <React.Fragment key={i}>
                               <NodeGroup entities={group} />
                                {i < nodegroups.length - 1 && (
                                    <div className='arrow'>→</div>
                                )}
                            </React.Fragment>
                        )
                    )
                }
            </div>
        </>
    )
}

export default Chart