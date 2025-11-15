import { useState } from "react";

async function getItems(
    sequenceArray,
    outputItemsState,
    setOutputItemsState
){
    const url = "https://api.ladlorchart.com/sequence/"; // Remote
    // const url = "http://127.0.0.1:8000/sequence/" // Localhost testing
    const flat = sequenceArray.flat();
    const keySet = new Set(Object.keys(outputItemsState));
    const payload = flat.filter(item => !keySet.has(item));;
    const clientCacheHits = flat.filter(item => keySet.has(item)).length;
    const clientCacheMisses = flat.length - clientCacheHits;
    console.log(`client hits: ${clientCacheHits}, client misses: ${clientCacheMisses}`);

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ sequence: payload })
        });
        if (!response.ok){
            throw new Error(`Response status: ${response.status}`);
        }
        const text = await response.text();
        console.log(text);

        // If you still want it as JSON afterwards:
        const result = JSON.parse(text);
        const items = result["items"];
        console.log(`cache hits: ${result["cacheHits"]}, cache misses: ${result["cacheMisses"]}`)
        setOutputItemsState(prev => ({ ...prev, ...items }));
    } catch (error) {
    console.error(error.message);
  }
}


export default function SequenceForm({
    setInputSequenceState,
    setOutputItemsState,
    outputItemsState
}){
    const [loading, setLoading] = useState(false);
    async function handleSubmit(e) {
        e.preventDefault();
        let raw = e.target.sequence.value.trim();

        if (!(raw.startsWith("[") && raw.endsWith("]"))) {
            console.log("Input not valid, must be list[list[str]]")
            return;
        }
        let sequenceArray;
        try {
            console.log(raw);
            sequenceArray = JSON.parse(raw);
            console.log(sequenceArray);
        } catch {
            console.log("Invalid JSON")
            return;
        }
        if (!(sequenceArray instanceof Array)){
        console.log("Not an Array");
        return;
        }
        // API expects list[list[str]], and user will be heldhand.
        sequenceArray.forEach((nodeGroup, index, array) => {
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
        setInputSequenceState(sequenceArray);
        setLoading(true);
        await getItems(sequenceArray, outputItemsState, setOutputItemsState);
        setLoading(false);
    }

  const style = {
    "display":"flex",
    "width":"100%",
    "flexDirection": "column"
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
        {loading && <p>Loading...</p>}
    </form>
  );
}
