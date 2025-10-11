
import { useLayoutEffect, useRef, useState } from 'react';

function ContextMenu({ entity, wikiUrl, onClose, onSkip, onHide, x, y}){
    // avoid menu screen clipping
    const ref = useRef(null);
    const [pos, setPos] = useState({ top: y, left: x });
    useLayoutEffect(() => {
        const el = ref.current;
        if (!el) return;
        const w = el.offsetWidth;
        const h = el.offsetHeight;
        const maxX = document.documentElement.clientWidth;
        const maxY = window.innerHeight + window.scrollY;

        let posX = x - w / 2;
        let posY = y;
        if (posX + w > maxX) posX = maxX - w;
        if (posX < 0) posX = 0;
        if (posY + h > maxY) posY = maxY - h;
        if (posY < window.scrollY) posY = window.scrollY;

        setPos({ top: posY, left: posX });
    }, [x, y]);
    return (
        <>
        <div
            ref={ref}
            id='context-menu'
            style={{
                position:"absolute",
                top: `${pos.top}px`,
                left: `${pos.left}px`,
                display: "block"
            }}
        >
            <div id='menu-title'>{entity}</div>
            <div id='button-container'>
                <button
                    id='wiki-button' 
                    className='menu-button'
                    onClick={() => {
                        window.open(wikiUrl, "_blank");
                        onClose();
                    }}
                >
                    <span className='left-text'>go to </span>
                    <span className='right-text'>Wiki</span>
                </button>
                <button 
                    id='skip-button'
                    className='menu-button'
                    onClick={() => {
                        onSkip(entity);
                        onClose();
                    }}
                >
                    <span className='left-text'>Mark as </span>
                    <span className='right-text'>Skipped</span>
                </button>
                <button
                    id='hide-button'
                    className='menu-button'
                    onClick={() => {
                        onHide(entity);
                        onClose;
                    }}
                >
                    <span className='left-text'>Hide</span>
                </button>
                <button
                    id='cancel-button'
                    className='menu-button'
                    onClick={onClose}
                >
                    <span className='left-text'>Cancel</span>
                </button>
            </div>
        </div>
        </>
    )
}

export default ContextMenu