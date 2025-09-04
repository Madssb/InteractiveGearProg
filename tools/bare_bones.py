import json
from pathlib import Path

ROOT_DIR = Path(__file__).parents[1]
FULL_PATH = ROOT_DIR / Path("data/sequence.json")
OUT_PATH = ROOT_DIR / Path("data/generated/sequence-bare-bones.json")

# Items to exclude when generating bare-bones
EXCLUDED = {
    "69 slayer",
    "Alchemist's amulet",
    "Amulet of glory",
    "Ash sanctifier",
    "Basic jewellery box",
    "Bigger and Badder",
    "Bonecrusher",
    "Broader Fletching",
    "Dark altar (Construction)",
    "Fairy ring (Construction)",
    "Greater Challenge",
    "Herb sack",
    "Karamja gloves 3",
    "Karamja gloves 4",
    "Occult altar",
    "Ornate jewellery box",
    "Ornate rejuvenation pool",
    "Prescription goggles",
    "Rejuvenation pool",
    "Reptile Got Ripped",
    "Spirit tree (Construction)",
    "Wrath rune",
    "gem bag",
    "hallowed crystal shard",
}


def make_bare_bones():
    FULL_PATH = ROOT_DIR / Path("data/sequence.json")
    OUT_PATH = ROOT_DIR / Path("data/generated/sequence-bare-bones.json")
    with FULL_PATH.open(encoding="utf-8") as f:
        seq_full = json.load(f)

    # Drop excluded items from each group
    bare = []
    for group in seq_full:
        new_group = [item for item in group if item not in EXCLUDED]
        if new_group:  # keep non-empty groups
            bare.append(new_group)

    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(bare, f, indent=4, ensure_ascii=False)


make_bare_bones()
