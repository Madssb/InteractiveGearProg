
import '@/styles/context-menu.css';
import { handleLevels } from '@/utils/textSanitizers';
import { useLayoutEffect, useRef, useState } from 'react';

export default function ContextMenu({ milestone, onClose, onHide, onDelete, onShowAnnotations, milestoneMetadata, x, y}){
    
    let wikiUrl = milestoneMetadata[handleLevels(milestone)]["wikiUrl"];
    let milestoneId = milestoneMetadata[handleLevels(milestone)]["id"];
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
            <div id='menu-title'>{milestone}</div>
            <div id='button-container'>
                    {wikiUrl && <button
                    id='wiki-button' 
                    className='menu-button'
                    onClick={() => {
                        window.open(wikiUrl, "_blank");
                        onClose();
                    }}
                >
                    <span className='left-text'>go to </span>
                    <span className='right-text'>Wiki</span>
                </button>}
                {onDelete && (
                    <button
                        id='delete-button'
                        className='menu-button'
                        onClick={() => {
                            onDelete(milestone);
                            onClose();
                        }}
                    >
                        <span className='left-text'>Delete </span>
                        <span className='right-text'>{milestone}</span>
                    </button>
                )}
                {onShowAnnotations && (
                    <button
                        id='annotation-button'
                        className='menu-button'
                        onClick={() => {
                            onShowAnnotations(milestone);
                            onClose();
                        }}
                    >
                        <span className='left-text'>Show </span>
                        <span className='right-text'>Annotations</span>
                    </button>
                )}
                {onShowAnnotations && (
                    <button
                        id='copy-id-button'
                        className='menu-button'
                        onClick={async () => {
                            try {
                                await navigator.clipboard.writeText(String(milestoneId));
                            } catch (err) {
                                console.error("Failed to copy milestone ID", err);
                            }
                            onClose();
                        }}
                    >
                        <span className='left-text'>Copy </span>
                        <span className='right-text'>ID</span>
                    </button>
                )}
                {onHide && (
                    <button
                        id='hide-button'
                        className='menu-button'
                        onClick={() => {
                            onHide(milestone);
                            onClose();
                        }}
                    >
                        <span className='left-text'>Hide</span>
                    </button>
                )}
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
