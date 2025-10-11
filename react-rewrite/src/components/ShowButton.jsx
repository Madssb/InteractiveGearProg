function ShowButton({ onShow, nodeVisibilities }){
    if (Object.keys(nodeVisibilities).length > 0) {
        return (
            <>
                <button
                    id="show-button"
                    onClick={onShow}
                >
                    <span id="show-text">Show hidden items</span>
                </button>
            </>
        )
    } else {
        return null;
    }
}
export default ShowButton;