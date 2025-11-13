async function getItems(inputSequenceState, setOutputNodeGroupState){
    const url = "http://127.0.0.1:8000/sequence/";
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ sequence: inputSequenceState })
        });
        if (!response.ok){
            throw new Error(`Response status: ${response.status}`);
        }
        const result = await response.json();
        const items = result["items"];
        setOutputNodeGroupState(items);
    } catch (error) {
    console.error(error.message);
  }
}


export default function SequenceForm({
    inputSequenceState,
    setInputSequenceState,
    setOutputItemsState
}){
  function handleSubmit(e) {
    e.preventDefault();
    let raw = e.target.sequence.value.trim();

    if (!(raw.startsWith("[") && raw.endsWith("]"))) {
        console.log("Input not valid, must be list[list[str]]")
        return;
    }
    let arr;
    try {
        arr = JSON.parse(raw)
    } catch {
        console.log("Invalid JSON")
        return;
    }
    if (!(arr instanceof Array)){
       console.log("Not an Array");
       return;
    }
    // API expects list[list[str]], and user will be heldhand.
    arr.forEach((nodeGroup, index, array) => {
        if (!(nodeGroup instanceof Array)){
            console.log(`Input must be list[list[str]], got: ${nodeGroup} (index${index})`)
            return;
        }
        nodeGroup.forEach((node, index2, array2) => {
            if (!(typeof node === "string")){
                console.log(`Input must be list[list[str]], got: ${node} (in ${nodeGroup})`)
                return;
            }
        })
    })
    setInputSequenceState(arr);
    getItems(arr, setOutputItemsState);


  }

  const style = {
    "display":"flex",
    "width":"100%",
    "flex-direction": "column"
  }
  return (
    <form onSubmit={handleSubmit} style={style}>
      <label htmlFor="sequence">Sequence:</label>
        <textarea
            id="sequence"
            className="sequence"
            rows={10}
            style={{ width: "100%" }}
            autoComplete="off"
        ></textarea>
      <input type="submit" value="Submit" />
    </form>
  );
}
