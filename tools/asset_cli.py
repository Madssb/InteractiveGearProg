"""CLI for asset management and status inspection."""

import json
from argparse import ArgumentParser
from pathlib import Path

from id_asset import IdAsset
from manual_asset import ManualAsset

ROOT_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = Path(ROOT_DIR / "frontend/public")
NAMES_JSON_PATH = Path(ROOT_DIR / "data/cache/names.json")
METADATA_PATH = Path(ROOT_DIR / "data/generated/milestone-metadata.json")
BASE = "https://oldschool.runescape.wiki/w/"


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


def unresolved_milestones():
    """prints resolved status on milestones

    Current coverage is id-matched and prayer icon path matched.
    """
    milestones = load_milestones()
    non_id_matched_milestones: list[str] = []
    for milestone in milestones:
        try:
            _ = IdAsset(milestone)
        except ValueError:
            non_id_matched_milestones.append(milestone)

    non_manual_matched_milestones: list[str] = []
    for milestone in non_id_matched_milestones:
        try:
            _ = ManualAsset(milestone)
        except ValueError:
            non_manual_matched_milestones.append(milestone)
    for milestone in non_manual_matched_milestones:
        print(milestone)


def get_assets():
    """Downloads missing assets from runelite cache.

    Currently supports only ingame item id tagged assets.
    """
    milestones = load_milestones()
    for milestone in milestones:
        try:
            ms = IdAsset(milestone)
            try:
                ms.get_asset()
            except FileExistsError:
                print(f"{ms.milestone} already on disk: {ms.path}. Skipping.")
        except ValueError:
            print(f"{milestone} not found in runelite static cache. Ignoring.")


def check_assets():
    """Check if all assets corresponding to a milestone exists on disk at expected path.

    Raises:
        FileNotFoundError: One or more assets are missing.
    """
    milestones = load_milestones()
    not_on_disk: list[str] = []
    not_on_disk_manual: list[str] = []

    for milestone in milestones:
        try:
            ms = IdAsset(milestone)
            if not ms.path.exists():
                # Confirmed absent from disk
                not_on_disk.append(milestone)
        except ValueError:
            # milestone is not an ID Asset. Retrying on manual assets:
            try:
                ms = ManualAsset(milestone)
            except FileNotFoundError:
                not_on_disk_manual.append(milestone)
    both = not_on_disk + not_on_disk_manual
    if len(both) > 0:
        raise FileNotFoundError(f"Files missing for\n{'\n'.join(both)}")


def build_metadata():
    """Construct metadata file for milestones.

    Raises:
        FileNotFoundError: If one or more assets corresponding to a milestone is missing.
    """
    check_assets()
    milestones = load_milestones()
    metadata = {}

    for milestone in milestones:
        try:
            ms = IdAsset(milestone)
        except ValueError:
            ms = ManualAsset(milestone)

        path = ms.path
        relative = path.relative_to(IMAGES_DIR)
        row = {
            "imgUrl": "/" + str(relative),
            "wikiUrl": BASE + ms.milestone.replace(" ", "_").lower(),
        }
        metadata[milestone] = row
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)


def check_metadata():
    """Validate metadata"""
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        metadata = set(json.load(f).keys())
    milestones = set(load_milestones())
    if not milestones.issubset(metadata):
        diff = milestones - metadata
        raise ValueError(
            "Milestones are not a subset of metadata keys. missing from metadata: ",
            " ".join(diff),
        )


def main():
    fns = {
        "get-assets": get_assets,
        "check-assets": check_assets,
        "unresolved": unresolved_milestones,
        "build-metadata": build_metadata,
    }
    parser = ArgumentParser(description="TBA")
    parser.add_argument(
        "mode",
        choices=fns.keys(),
    )
    args = parser.parse_args()
    fns[args.mode]()


if __name__ == "__main__":
    main()
