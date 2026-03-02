/**
 * Convert an OSRS quest name into initials.
 */
export function questNameInitials(name) {
    const QUEST_ALIASES = {
        "The Ribbiting Tale of a Lily Pad Labour Dispute": "FROG",
    };

    const WORD_PATTERN = /[A-Za-z0-9]+(?:'[A-Za-z0-9]+)*/g;
    const RFD_FREEING_PATTERN = /^Recipe for Disaster\/Freeing(?: the)?\s+(.+)$/i;

    if (typeof name !== "string") {
        return "";
    }

    const alias = QUEST_ALIASES[name];
    if (alias) {
        return alias;
    }

    function normalizeTrailingRomanNumeral(input) {
        return input.replace(/\b(II|I)\s*$/, (_fullMatch, roman) => {
            return roman === "II" ? "2" : "1";
        });
    }

    function initialsFromTokens(input) {
        const tokens = input.match(WORD_PATTERN) || [];
        if (tokens.length === 0) {
            return "";
        }
        return tokens.map((token) => token[0].toUpperCase()).join("");
    }

    const rfdMatch = name.trim().match(RFD_FREEING_PATTERN);
    if (rfdMatch) {
        const freedTarget = normalizeTrailingRomanNumeral(rfdMatch[1]);
        const suffix = initialsFromTokens(freedTarget);
        return `RFD${suffix}`;
    }

    const normalizedName = normalizeTrailingRomanNumeral(name);
    return initialsFromTokens(normalizedName);
}
