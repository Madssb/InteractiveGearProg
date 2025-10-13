export default function ShowButton({ onShow }){
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
}
