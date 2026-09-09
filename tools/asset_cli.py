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
MILESTONE_IDS_PATH = Path(ROOT_DIR / "data/logic/milestone-ids.json")
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


def save_milestone_ids(milestone_ids: dict[int, str]) -> None:
    """Persist immutable milestone ids sorted numerically for stable diffs."""
    MILESTONE_IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    serializable_ids = {
        str(milestone_id): milestone_ids[milestone_id]
        for milestone_id in sorted(milestone_ids)
    }
    with MILESTONE_IDS_PATH.open("w", encoding="utf-8") as f:
        json.dump(serializable_ids, f, indent=2, ensure_ascii=False)
        f.write("\n")


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


def check_ids():
    """Validate there exists an ID for all milestones.

    Raises:
        FileNotFoundError: Milestone-ids json not found.
        ValueError: milestones are missing from the IDs json.
    """
    if not MILESTONE_IDS_PATH.exists():
        raise FileNotFoundError(
            "Milestone IDs json not found. Expected: ", MILESTONE_IDS_PATH
        )
    with open(MILESTONE_IDS_PATH, "r") as f:
        milestone_ids: dict = json.load(f)
    ided_milestones = set(milestone_ids.values())
    milestones = set(load_milestones())
    if not milestones.issubset(ided_milestones):
        diff = milestones - ided_milestones
        raise ValueError(
            "Milestones are not a subset of ID vals. missing from IDs: ",
            " ".join(diff),
        )


def build_ids():
    """Update ID Json with unseen milestones.

    Raises:
        FileNotFoundError: Milestone-ids json not found.
        ValueError: ID dict edit would overwrite existsing key.
    """
    if not MILESTONE_IDS_PATH.exists():
        raise FileNotFoundError("Milestone IDs not found.")
    with open(MILESTONE_IDS_PATH, "r") as f:
        milestone_ids: dict = json.load(f)
    ided_milestones = set(milestone_ids.values())
    milestones = set(load_milestones())
    if milestones.issubset(ided_milestones):
        with open(MILESTONE_IDS_PATH, "w") as f:
            json.dump(milestone_ids, f, indent=2)
        return
    max_idx = max(int(idx) for idx in milestone_ids)

    non_ided_milestones = milestones - ided_milestones
    # start from next index and pad
    for idx, ms in zip(
        range(max_idx + 1, max_idx + 1 + len(non_ided_milestones)),
        list(non_ided_milestones),
    ):
        if str(idx) in milestone_ids:
            raise ValueError("Would override on ", idx)
        milestone_ids[str(idx)] = ms
    with open(MILESTONE_IDS_PATH, "w") as f:
        json.dump(milestone_ids, f, indent=2)


def build_metadata():
    """Construct metadata file for milestones.

    Raises:
        FileNotFoundError: Milestone metadata json not found.
    """
    try:
        check_assets()
    except ValueError:
        build_ids()
    milestones = load_milestones()
    metadata = {}
    with open(MILESTONE_IDS_PATH, "r") as f:
        milestone_ids: dict = json.load(f)

    # id:milestone is bijective
    id_lut = {v: k for k, v in milestone_ids.items()}

    for milestone in milestones:
        try:
            ms = IdAsset(milestone)
        except ValueError:
            ms = ManualAsset(milestone)

        path = ms.path
        relative = path.relative_to(IMAGES_DIR)
        row = {
            "imgUrl": "/" + str(relative),
            "type": ms.type,
            "id": id_lut[milestone],
        }
        # lvl milestones deviate in intended wiki url behavior.
        if ms.wiki_url is not None:
            row["wikiUrl"] = ms.wiki_url
        metadata[milestone] = row
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)


def check_metadata():
    """Validate there exists metadata records for all milestones.

    Raises:
        FileNotFoundError: Milestone metadata json not found.
        ValueError: milestones records are missing from the metadata json.
    """
    check_ids()
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Milestone metadata json not found. Expected: ", METADATA_PATH
        )
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
        "check-ids": check_ids,
        "build-ids": build_ids,
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
