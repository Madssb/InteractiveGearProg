
function ContextMenu({ title, wikiUrl, onClose, onSkip, x, y}){
    return (
        <>
        <div
            id='context-menu'
            style={{
                position:"absolute",
                top: `${y}px`,
                left: `${x}px`,
                display: "block"
            }}
        >
            <div id='menu-title'>{title}</div>
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
                        onSkip?.();
                        onClose();
                    }}
                >
                    <span className='left-text'>Mark as </span>
                    <span className='right-text'>Skipped</span>
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