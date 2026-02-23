const MANUAL_FIXES = {
  "ghommals-hilt-5": "Ghommal's hilt 5",
  "masori-mask-f": "Masori mask (f)",
  "masori-body-f": "Masori body (f)",
  "masori-chaps-f": "Masori chaps (f)",
  "ring-of-suffering-i": "Ring of suffering (i)",
  "ghommals-hilt-4": "Ghommal's hilt 4",
  "mystic-vigour": "Mystic Vigour",
  "alchemists-amulet": "Alchemist's amulet",
  "greater-challenge": "Greater Challenge",
  "reptile-got-ripped": "Reptile Got Ripped",
  "slayer-helmet-i": "Slayer helmet (i)",
  "explorers-ring-4": "Explorer's ring 4",
  "spellbook-swap": "Spellbook Swap",
  "bow-of-faerdhinen-c": "Bow of faerdhinen (c)",
  "lvl-92-ranged": "92 ranged",
  "lvl-86-strength": "86 strength",
  "ghommals-hilt-2": "Ghommal's hilt 2",
  "broader-fletching": "Broader Fletching",
  "lvl-69-slayer": "69 slayer",
  "lvl-70-ranged": "70 ranged",
  "mages-book": "Mage's book",
  "ice-barrage": "Ice Barrage",
  "bigger-and-badder": "Bigger and Badder",
  "black-mask-i": "Black mask (i)",
  "imbued-zamorak-cape": "Imbued Zamorak cape",
  "gem-bag": "Gem bag",
  "berserker-ring-i": "Berserker ring (i)",
  "ibans-staff-u": "Iban's staff (u)",
  "protect-from-melee": "Protect from Melee",
  "eagle-eye": "Eagle Eye",
  "avas-accumulator": "Ava's accumulator",
  "avas-assembler": "Ava's assembler",
  "spirit-tree-construction": "Spirit tree (Construction)",
  "dark-altar-construction": "Dark altar (Construction)",
  "fairy-ring-construction": "Fairy ring (Construction)",
  "radas-blessing-4": "Rada's blessing 4",
  "pharaohs-sceptre": "Pharaoh's sceptre",
  "osmumtens-fang": "Osmumten's fang",
  "dizanas-quiver": "Dizana's quiver",
  "tumekens-shadow": "Tumeken's shadow",
  "elidinis-ward": "Elidinis' ward"
};

function simpleTransform(id) {
  if (MANUAL_FIXES[id]) return MANUAL_FIXES[id];
  const words = id.split("-");
  words[0] = words[0].charAt(0).toUpperCase() + words[0].slice(1);
  return words.join(" ");
}

export default function migrateLegacySharedNodeStates(setNodesCompleteState) {
  if (localStorage.getItem("nodesCompleteState")) return;
  const legacy = localStorage.getItem("sharedNodeStates");
  if (!legacy) return;

  try {
    let parsed = JSON.parse(legacy);
    if (typeof parsed === "string") parsed = JSON.parse(parsed);

    const migrated = Object.keys(parsed)
      .filter(k => parsed[k] === 1)
      .map(simpleTransform);

    setNodesCompleteState(new Set(migrated));
    localStorage.setItem("nodesCompleteState", JSON.stringify(migrated));
    localStorage.setItem("migrationDone", "true");
    console.log(`Migrated ${migrated.length} nodes`);
  } catch (err) {
    console.error("Failed migration:", err);
  }
}
