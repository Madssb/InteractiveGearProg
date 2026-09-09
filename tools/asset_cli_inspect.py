"""CLI for inspection of runelite cache properties"""

import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
from id_asset import IdAsset

ROOT_DIR = Path(__file__).resolve().parent.parent
NOTES_PATH = Path(ROOT_DIR / "data/cache/notes.json")
with NOTES_PATH.open() as r:
    NOTES = json.load(r)


def load_json(path: Path) -> list:
    """Load JSON-file."""
    if not path.exists():
        raise FileNotFoundError("JSON not found: ", path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_milestones() -> list[str]:
    """Load all milestones."""
    sequence_sources = [
        Path(ROOT_DIR / "data/logic/milestone-sequence-main.json"),
        Path(ROOT_DIR / "data/logic/milestone-sequence-retirement.json"),
    ]
    items_nested = []
    for path in sequence_sources:
        items_nested.extend(load_json(path))
    milestones = [item for group in items_nested for item in group]
    return milestones


def item_ids(milestone: str):
    """Show item ids for milestone per the static runelite cache."""
    item_ids = IdAsset(milestone).all_item_ids()
    print("milestone: " + " ".join(item_ids))


def multiplicity():
    """Show multiplicity of all milestones."""
    milestones = load_milestones()
    multiplicity = {}
    for milestone in milestones:
        try:
            multiplicity[milestone] = len(IdAsset(milestone).all_item_ids())
        except ValueError:
            pass
    multiplicity = pd.Series(multiplicity)
    for i in range(1, int(multiplicity.max()) + 1):
        print(i, ":")
        print("\t", "\n\t".join(multiplicity.index[multiplicity == i].tolist()))


def asset_urls(milestone: str):
    """Show all asset source urls for milestone."""
    urls = IdAsset(milestone).asset_urls()
    print(f"Asset source urls for {milestone}:\n\t" + "\n\t".join(urls))


def inspect_notes():
    """
    Hypothesis: All
    """
    one_diff_count = 0
    key_is_lower_count = 0
    key_is_higher_count = 0
    for key in NOTES:
        if abs(NOTES[key] - int(key)) == 1:
            one_diff_count += 1
            if int(key) > NOTES[key]:
                key_is_higher_count += 1
            else:
                key_is_lower_count += 1
    print("one diff count: ", one_diff_count)
    print("key is lower: ", key_is_lower_count)
    print("key is higher: ", key_is_higher_count)
    print("total: ", len(NOTES.keys()))


def main():
    fns = {
        "item_ids": item_ids,
        "multiplicity": multiplicity,
        "asset-urls": asset_urls,
        "inspect-notes": inspect_notes,
    }
    parser = ArgumentParser(description="TBA")
    parser.add_argument(
        "mode",
        choices=fns.keys(),
    )
    parser.add_argument("milestone", nargs="?")
    args = parser.parse_args()
    try:
        fns[args.mode]()
    except TypeError:
        fns[args.mode](args.milestone)


if __name__ == "__main__":
    main()
