import { useState } from "react";

/**
 * Fetches metadata for items that are not already in local cache state.
 * Throws on request/parse errors so the form can show a user-facing message.
 */
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

        // If you still want it as JSON afterwards:
        const result = JSON.parse(text);
        const items = result["items"];
        // console.log(`cache hits: ${result["cacheHits"]}, cache misses: ${result["cacheMisses"]}`)
        setOutputItemsState(prev => ({ ...prev, ...items }));
    } catch (error) {
        console.error(error.message);
        throw error;
    }
}

/**
 * Splits input by top-level commas/newlines while respecting brackets/quotes.
 *
 * Example:
 * - `a, [b, c], "d,e"` => ["a", "[b, c]", "\"d,e\""]
 *
 * Apostrophe rule:
 * - `cook's assistant` should stay one raw token (apostrophe is literal).
 * - `'quoted value'` still works when quote starts the token.
 */
function splitTopLevel(input) {
    const tokens = [];
    let current = "";
    let bracketDepth = 0;
    let quote = null;
    let escaped = false;

    for (let i = 0; i < input.length; i += 1) {
        const char = input[i];

        if (escaped) {
            current += char;
            escaped = false;
            continue;
        }
        if (char === "\\") {
            current += char;
            escaped = true;
            continue;
        }
        if (quote) {
            current += char;
            if (char === quote) quote = null;
            continue;
        }
        // Only treat apostrophe as a quote when it starts a token.
        // This keeps common text like "cook's assistant" unquoted-friendly.
        const isTokenStart = current.trim().length === 0;
        if (char === "\"" || (char === "'" && isTokenStart)) {
            current += char;
            quote = char;
            continue;
        }
        if (char === "[") {
            bracketDepth += 1;
            current += char;
            continue;
        }
        if (char === "]") {
            bracketDepth -= 1;
            if (bracketDepth < 0) throw new Error("Unexpected closing bracket.");
            current += char;
            continue;
        }
        if ((char === "," || char === "\n") && bracketDepth === 0) {
            const token = current.trim();
            if (token) tokens.push(token);
            current = "";
            continue;
        }
        current += char;
    }

    if (quote) throw new Error("Unclosed quote.");
    if (bracketDepth !== 0) throw new Error("Unclosed bracket group.");

    const trailing = current.trim();
    if (trailing) tokens.push(trailing);
    return tokens;
}

/**
 * Parses one token as either:
 * - quoted string: "text" or 'text'
 * - raw text: text
 */
function parseQuotedOrRaw(value) {
    const trimmed = value.trim();
    if (!trimmed) return null;

    const startsQuote = trimmed.startsWith("\"") || trimmed.startsWith("'");
    const endsQuote = trimmed.endsWith("\"") || trimmed.endsWith("'");
    if (startsQuote || endsQuote) {
        if (!startsQuote || !endsQuote || trimmed[0] !== trimmed[trimmed.length - 1]) {
            throw new Error(`Malformed quoted value: ${trimmed}`);
        }
        return trimmed.slice(1, -1).trim();
    }
    return trimmed;
}

/**
 * Ensures backend contract: always returns string[][]
 *
 * Accepts:
 * - ["a", ["b", "c"]] and normalizes to [["a"], ["b", "c"]]
 * Rejects:
 * - non-array roots, non-string values, empty strings/groups
 */
function normalizeParsedSequence(sequence) {
    if (!(sequence instanceof Array)) throw new Error("Input must be an array.");

    const normalized = sequence.map((group, index) => {
        if (typeof group === "string") {
            const value = group.trim();
            if (!value) throw new Error(`Empty item at position ${index + 1}.`);
            return [value];
        }
        if (!(group instanceof Array)) {
            throw new Error(`Entry ${index + 1} must be a string or list of strings.`);
        }

        const normalizedGroup = group.map((item, itemIndex) => {
            if (typeof item !== "string") {
                throw new Error(`Group ${index + 1}, item ${itemIndex + 1} must be text.`);
            }
            const value = item.trim();
            if (!value) {
                throw new Error(`Group ${index + 1}, item ${itemIndex + 1} cannot be empty.`);
            }
            return value;
        });

        if (normalizedGroup.length === 0) throw new Error(`Group ${index + 1} cannot be empty.`);
        return normalizedGroup;
    });

    if (normalized.length === 0) throw new Error("At least one item is required.");
    return normalized;
}

/**
 * Flexible input parser for the Sequence textarea.
 *
 * Supported forms:
 * 1) Strict JSON
 *    `[["abyssal whip"], ["cake", "rune scimitar"]]`
 * 2) JSON-like fragment
 *    `"abyssal whip", ["cake", "rune scimitar"], "dragon bones"`
 * 3) Relaxed text
 *    `abyssal whip, [cake, rune scimitar], dragon bones`
 *
 * Note: apostrophes inside words are treated as literal characters, so
 * `cook's assistant` works without quotes.
 */
function parseFlexibleSequenceInput(raw) {
    const trimmed = raw.trim();
    if (!trimmed) throw new Error("Please enter at least one item.");

    // Keep existing JSON input support.
    try {
        return normalizeParsedSequence(JSON.parse(trimmed));
    } catch {
        // ignored: we'll try relaxed parsing
    }

    // Support list fragments like: "a", ["b", "c"], "d"
    try {
        return normalizeParsedSequence(JSON.parse(`[${trimmed}]`));
    } catch {
        // ignored: we'll try non-JSON parsing
    }

    // Relaxed parser: allow unquoted values and bracket groups.
    const topLevelEntries = splitTopLevel(trimmed);
    if (topLevelEntries.length === 0) throw new Error("Please enter at least one item.");

    const sequence = topLevelEntries.map((entry, entryIndex) => {
        const token = entry.trim();
        if (token.startsWith("[") || token.endsWith("]")) {
            if (!(token.startsWith("[") && token.endsWith("]"))) {
                throw new Error(`Malformed group at position ${entryIndex + 1}.`);
            }
            const inner = token.slice(1, -1).trim();
            if (!inner) throw new Error(`Group ${entryIndex + 1} cannot be empty.`);
            const groupTokens = splitTopLevel(inner);
            if (groupTokens.length === 0) throw new Error(`Group ${entryIndex + 1} cannot be empty.`);
            return groupTokens.map((part) => {
                const value = parseQuotedOrRaw(part);
                if (!value) throw new Error(`Group ${entryIndex + 1} contains an empty item.`);
                return value;
            });
        }

        const value = parseQuotedOrRaw(token);
        if (!value) throw new Error(`Empty item at position ${entryIndex + 1}.`);
        return [value];
    });

    return sequence;
}


export default function SequenceForm({
    setInputSequenceState,
    setOutputItemsState,
    outputItemsState
}){
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    /**
     * Parses, normalizes, stores, then fetches metadata for new items.
     * Any thrown errors become inline messages under the form.
     */
    async function handleSubmit(e) {
        e.preventDefault();
        setError("");
        const raw = e.target.sequence.value.trim();

        let sequenceArray;
        try {
            sequenceArray = parseFlexibleSequenceInput(raw);
        } catch (parseError) {
            setError(parseError.message);
            return;
        }

        setInputSequenceState(sequenceArray);
        try {
            setLoading(true);
            await getItems(sequenceArray, outputItemsState, setOutputItemsState);
        } catch {
            setError("Could not fetch item metadata from backend. Please try again.");
        } finally {
            setLoading(false);
        }
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
            placeholder={`Examples:\n"abyssal whip", ["cake", "rune scimitar"], "dragon bones"\nabyssal whip, [cake, rune scimitar], dragon bones\n[["abyssal whip"], ["cake", "rune scimitar"], ["dragon bones"]]`}
        ></textarea>
        <input type="submit" value="Submit" />
        {error && <p style={{ color: "crimson" }}>{error}</p>}
        {loading && <p>Loading...</p>}
    </form>
  );
}
