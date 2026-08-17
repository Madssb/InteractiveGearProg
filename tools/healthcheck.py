from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

import requests
from osrs_milestone_metadata.client import TIMEOUT
from osrs_milestone_metadata.client import s as wiki_session
from pydantic import TypeAdapter, ValidationError

from osrs_milestone_metadata import MilestoneMetadata

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METADATA_PATH = REPO_ROOT / "data/generated/milestone-metadata.json"
MILESTONE_SEQUENCE_PATHS = [
    REPO_ROOT / "data/logic/milestone-sequence-main.json",
    REPO_ROOT / "data/logic/milestone-sequence-retirement.json",
]
LEVEL_RE = re.compile(r"\d+ (\w+)")


def load_milestone_metadata(path: Path) -> MilestoneMetadata:
    with path.open("r", encoding="utf-8") as f:
        raw_metadata = json.load(f)

    try:
        return TypeAdapter(MilestoneMetadata).validate_python(raw_metadata)
    except ValidationError as exc:
        raise ValueError(
            f"{path} does not contain valid milestone metadata: {exc}"
        ) from exc


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def milestone_metadata_key(milestone: str) -> str:
    milestone = milestone.lstrip("*")
    match = LEVEL_RE.match(milestone)
    if match:
        return match.group(1)
    return milestone


def load_sequence_milestones(paths: list[Path]) -> list[str]:
    milestones = []

    for path in paths:
        raw_groups = load_json(path)
        if not isinstance(raw_groups, list):
            raise ValueError(f"{path} must contain a list of milestone groups")

        for raw_group in raw_groups:
            if not isinstance(raw_group, list):
                raise ValueError(f"{path} must contain nested milestone lists")
            for raw_milestone in raw_group:
                if not isinstance(raw_milestone, str):
                    raise ValueError(f"{path} contains a non-string milestone")
                milestones.append(milestone_metadata_key(raw_milestone))

    return list(dict.fromkeys(milestones))


def select_milestones(milestones: list[str], sample_size: int | None) -> list[str]:
    if sample_size is None:
        return milestones
    if sample_size < 1:
        raise ValueError("--sample-size must be positive")
    if sample_size >= len(milestones):
        return milestones
    return sorted(random.sample(milestones, sample_size))


def check_img_url(milestone: str, img_url: str) -> str | None:
    try:
        response = wiki_session.head(img_url, allow_redirects=True, timeout=TIMEOUT)
    except requests.RequestException as exc:
        return f"{milestone}: request failed for {img_url}: {exc}"

    if response.status_code == 429:
        return f"{milestone}: rate limited checking {img_url}"
    if response.status_code >= 400:
        return f"{milestone}: {img_url} returned HTTP {response.status_code}"
    return None


def check_metadata_img_urls(
    path: Path, milestones_to_check: list[str] | None
) -> list[str]:
    metadata = load_milestone_metadata(path)
    failures = []
    checkable_metadata = metadata

    if milestones_to_check is not None:
        missing_milestones = [
            milestone for milestone in milestones_to_check if milestone not in metadata
        ]
        if missing_milestones:
            raise ValueError(
                f"sequence milestone(s) missing from metadata: {missing_milestones}"
            )
        checkable_metadata = {
            milestone: metadata[milestone] for milestone in milestones_to_check
        }

    for milestone, record in checkable_metadata.items():
        failure = check_img_url(milestone, str(record.imgUrl))
        if failure is not None:
            failures.append(failure)

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate generated milestone metadata image URLs."
    )
    parser.add_argument(
        "--metadata-path",
        type=Path,
        default=DEFAULT_METADATA_PATH,
        help="path to milestone-metadata.json",
    )
    parser.add_argument(
        "--sequence-only",
        action="store_true",
        help="only check milestones from milestone-sequence-main and retirement",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        help="randomly check this many sequence milestones",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="random seed used with --sample-size",
    )
    args = parser.parse_args()

    try:
        random.seed(args.seed)
        sequence_milestones = None
        if args.sequence_only or args.sample_size is not None:
            sequence_milestones = select_milestones(
                load_sequence_milestones(MILESTONE_SEQUENCE_PATHS),
                args.sample_size,
            )
        failures = check_metadata_img_urls(args.metadata_path, sequence_milestones)
    except Exception as exc:
        print(f"healthcheck failed: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("Invalid milestone metadata image URL(s):", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        f"OK: all milestone metadata image URLs are reachable in {args.metadata_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
