import commonAliases from '@data/logic/common-aliases.json';

function normalizeAliasKey(input) {
    return input.trim().toLowerCase().replace(/\s+/g, " ");
}

const aliasLookup = Object.fromEntries(
    Object.entries(commonAliases).map(([alias, canonical]) => [normalizeAliasKey(alias), canonical])
);

export function resolveCommonAlias(input) {
    if (typeof input !== "string") return input;
    const key = normalizeAliasKey(input);
    return aliasLookup[key] || input;
}
