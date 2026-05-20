import json
import re
from pathlib import Path
from typing import List

from pydantic import TypeAdapter, ValidationError

from osrs_milestone_metadata import (
    MilestoneMetadata,
    query_milestone_metadata,
)

pat = re.compile(r"\d+ (\w+)")

WIKI_W = "https://oldschool.runescape.wiki/w/"
WIKI_IMG = "https://oldschool.runescape.wiki/images/"
IMG_EXT_RE = re.compile(r"\.(png|gif|jpg|jpeg|webp)$", re.IGNORECASE)
MILESTONE_IDS_PATH = Path("data/logic/milestone-ids.json")


def handle_levels(input: str):
    match = pat.match(input)
    if match:
        return match.group(1)
    return input


def sanitize_name_for_url(name: str) -> str:
    # Loose normalization to match typical wiki page path
    return name.strip().replace(" ", "_")


def load_json(path: Path) -> List:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_milestone_metadata() -> MilestoneMetadata:
    """Load and validate generated milestone metadata.

    Raises:
        ValueError: If the file cannot be parsed as MilestoneMetadata.
    """
    milestones_metadata_path = Path("data/generated/milestone-metadata.json")

    with milestones_metadata_path.open("r", encoding="utf-8") as f:
        raw_milestones_metadata = json.load(f)

    try:
        return TypeAdapter(MilestoneMetadata).validate_python(raw_milestones_metadata)
    except ValidationError as exc:
        raise ValueError(
            f"{milestones_metadata_path} does not contain valid milestone metadata: "
            f"{exc}"
        ) from exc


def load_milestone_ids() -> dict[int, str]:
    """Load immutable milestone ids.

    The file is shaped as `{id: milestone_name}` so API and bot code can resolve
    user-submitted ids directly. JSON object keys are strings on disk, so this
    converts them to ints and validates uniqueness.
    """
    raw_milestone_ids = load_json(MILESTONE_IDS_PATH)
    if raw_milestone_ids == {}:
        return {}
    if not isinstance(raw_milestone_ids, dict):
        raise ValueError(f"{MILESTONE_IDS_PATH} must contain an object of id-to-name pairs")

    milestone_ids: dict[int, str] = {}
    names_seen: set[str] = set()
    for raw_id, milestone in raw_milestone_ids.items():
        try:
            milestone_id = int(raw_id)
        except ValueError as exc:
            raise ValueError(f"{MILESTONE_IDS_PATH} contains a non-integer id: {raw_id}") from exc
        if milestone_id < 1:
            raise ValueError(f"{MILESTONE_IDS_PATH} contains a non-positive id: {milestone_id}")
        if not isinstance(milestone, str) or not milestone:
            raise ValueError(f"{MILESTONE_IDS_PATH} id {milestone_id} must map to a milestone name")
        if milestone_id in milestone_ids:
            raise ValueError(f"{MILESTONE_IDS_PATH} contains duplicate id: {milestone_id}")
        if milestone in names_seen:
            raise ValueError(f"{MILESTONE_IDS_PATH} contains duplicate milestone name: {milestone}")
        milestone_ids[milestone_id] = milestone
        names_seen.add(milestone)
    return milestone_ids


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


def ensure_milestone_ids(milestones: list[str]) -> dict[str, int]:
    """Ensure every milestone has an immutable id and return name-to-id mapping.

    Existing ids are never renumbered or removed. Milestones that no longer
    appear in generated metadata stay in `milestone-ids.json` so old annotation
    records keep a resolvable reference point.
    """
    milestone_ids = load_milestone_ids()
    id_by_milestone = {milestone: milestone_id for milestone_id, milestone in milestone_ids.items()}
    next_id = max(milestone_ids.keys(), default=0) + 1

    for milestone in milestones:
        if milestone in id_by_milestone:
            continue
        milestone_ids[next_id] = milestone
        id_by_milestone[milestone] = next_id
        next_id += 1

    save_milestone_ids(milestone_ids)
    return id_by_milestone


def load_milestones() -> list[str]:
    """Load milestones ready for metadata querying
    """
    milestone_sequence_sources = [
        Path("data/logic/milestone-sequence-main.json"),
        Path("data/logic/milestone-sequence-retirement.json"),
    ]
    items_nested = []
    for path in milestone_sequence_sources:
        items_nested.extend(load_json(path))
    milestones = [item for group in items_nested for item in group]
    milestones_stripped = [s.lstrip("*") for s in milestones]
    milestones_processed = []
    for item in milestones_stripped:
        milestones_processed.append(handle_levels(item))
    return milestones_processed


def generate_milestone_sequence_bare_bones():
    """milestone-sequence-bare-bones is derived by main chart milestone sequence
    filtered by filter.json.
    """
    milestone_sequence = load_json(Path("data/logic/milestone-sequence-main.json"))
    milestone_filter = set(load_json(Path("data/logic/filter.json")))

    milestone_sequence_bare_bones = []
    for milestone_group in milestone_sequence:
        filtered_group = [
            milestone
            for milestone in milestone_group
            if milestone not in milestone_filter
        ]
        if filtered_group:
            milestone_sequence_bare_bones.append(filtered_group)

    out = Path("data/generated/milestone-sequence-barebones.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(milestone_sequence_bare_bones, f, indent=2, ensure_ascii=False)


def update_milestone_metadata():
    """Ensure `data/generated/milestone-metadata.json` stays up to date with
    `data/logic/milestone-sequence-*`
    """
    milestones = load_milestones()
    milestones_metadata = load_milestone_metadata()
    milestones_not_in_metadata = set(milestones) - set(milestones_metadata.keys())

    
    res = query_milestone_metadata(milestones_not_in_metadata)
    if len(res.unresolvedMilestones) > 0:
        raise ValueError(f"One or more loaded milestones do not have valid metadata: {res.unresolvedMilestones}")
    milestones_metadata = milestones_metadata | res.milestoneMetadata
    milestone_ids = ensure_milestone_ids(list(milestones_metadata.keys()))

    out = Path("data/generated/milestone-metadata.json")
    serializable_metadata = {
        milestone: record.model_dump(mode="json") | {"id": milestone_ids[milestone]}
        for milestone, record in milestones_metadata.items()
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(serializable_metadata, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    update_milestone_metadata()
    generate_milestone_sequence_bare_bones()
