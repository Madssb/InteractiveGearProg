export default function TitleAndButtons( {children} ){
    const style = {"justify-content": "space-between", "display":"flex", "align-items": "center"}
    return (
        <div className="title-and-buttons" style={style}><div />{children}</div>
    )
}