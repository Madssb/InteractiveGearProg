export default function ShowButton({ onShow, buttonText }){
    return (
        <>
            <button
                id="show-button"
                onClick={onShow}
            >
                <span id="show-text">{buttonText}</span>
            </button>
        </>
    )
}
