type SequenceAndFormat  = {
    // Parsed user-submitted milestone sequence.
    sequence: string[][];
    // user submitted input uses quotes
    quotes: boolean;
}

/**
 * Get user-submitted milestone sequence from nested list of strings or with outer brackets missing.
 * @param inputText SequenceForm textbox input contents.
 * @returns User-submitted milestone sequence.
 * @throws {Error} If input parsing failed.
 */
function quotesFormatInput(inputText: string): string[][] {
    const stripped = inputText.trim();
    let parsed: unknown;
    
    // Identical check made up to two times if the first fails.
    function parsedChecks(parsed: any) {
        if (!Array.isArray(parsed)) {
            throw new Error("Sequence must be an array.");
        }

        if (parsed.length === 0) {
            throw new Error("Sequence cannot be empty.");
        }

        for (const group of parsed) {
            if (!Array.isArray(group) || group.length === 0) {
                throw new Error("Each group must be a non-empty array.");
            }

            for (const milestone of group) {
                if (typeof milestone !== "string" || milestone.trim() === "") {
                    throw new Error("Each milestone must be a non-empty string.");
                }
            }
        }
    }
    
    try {
        parsed = JSON.parse(stripped);
        parsedChecks(parsed);
    } catch {
        // user couldve missed outer brackets for valid json.
        try {
            parsed = JSON.parse(`[${stripped}]`);
            parsedChecks(parsed);
        } catch {
            // also not valid.
            throw new Error("Couldn't parse input.");
        }        
    }

    return parsed as string[][];
}

/**
 * Get sequence from non-json compliant input.
 * @param inputText SequenceForm textbox input contents.
 * @returns User-submitted milestone sequence.
 */
function noQuotesFormatInput(inputText: string): string[][] {
    const stripped = inputText.trim();
    
    // matches against [a], [a ], [ a ], [a,b], etc.
    // first group is a, a,b, etc.
    const group = /\[(\s*(?:[^,\[\]]+\s*,\s*)*(?:[^,\[\]]+)\s*)\]/g;
    
    // matches against '[  [ a ], [ c , d ]]', etc.
    const properFormat = new RegExp(
        `^\\[\\s*(?:${group.source}\\s*,\\s*)*(?:${group.source})\\s*\\]$`
    );

    // matches against '[ a  ],[ c , d ], [e,f,g]', etc.
    const looseFormat = new RegExp(
        `^(?:${group.source}\\s*,\\s*)*(?:${group.source})$`
    );
    
    if (!(properFormat.test(stripped) || looseFormat.test(stripped))) {
        throw new Error("Invalid format.");
    }
    const out: string[][] = [];
    const matches = [...stripped.matchAll(group)];
    for (const match of matches) {
        const group: string[] = [];
        // first group.
        const milestones = match[1].split(",")
        for (const milestone of milestones) {
            group.push(milestone.trim())
        }
        out.push(group);
    }
    return out;
}

/**
 * Get sequence where milestones arent input as strings
 * @param inputText SequenceForm textbox input contents.
 * @returns User-submitted milestone sequence.
 * @throws {Error} If input does not meet formatting requirements.
 */
export default function getSequenceFromInput(inputText: string): SequenceAndFormat {
    try {
        return {"sequence": quotesFormatInput(inputText), "quotes":true};
    } catch {
        try {
            return {"sequence": noQuotesFormatInput(inputText), "quotes":false};
        } catch {
            throw new Error(`Input text does not meet any of the formatting requirements: ${inputText}`)
        }
    }
}
