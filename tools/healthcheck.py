"""Validate chart metadata is not stale by trying out all urls"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests
from osrs_milestone_metadata.client import TIMEOUT
from osrs_milestone_metadata.client import s as wiki_session
from pydantic import TypeAdapter, ValidationError

from osrs_milestone_metadata import MilestoneMetadata

REPO_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = REPO_ROOT / "data/generated/milestone-metadata.json"
MILESTONE_SEQUENCE_PATHS = [
    REPO_ROOT / "data/logic/milestone-sequence-main.json",
    REPO_ROOT / "data/logic/milestone-sequence-retirement.json",
]
LEVEL_RE = re.compile(r"\d+ (\w+)")


def load_milestone_metadata() -> MilestoneMetadata:
    """Load metadata, reject if invalid."""
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        raw_metadata = json.load(f)

    try:
        return TypeAdapter(MilestoneMetadata).validate_python(raw_metadata)
    except ValidationError as exc:
        raise ValueError(
            f"{METADATA_PATH} does not contain valid milestone metadata: {exc}"
        ) from exc


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def milestone_metadata_key(milestone: str) -> str:
    """Normalize milestone elements for metadata lookup."""
    milestone = milestone.lstrip("*")
    match = LEVEL_RE.match(milestone)
    if match:
        return match.group(1)
    return milestone


def load_milestones() -> list[str]:
    """Load milestones for main chart, i.e. main-group and retirement home."""
    milestones = []

    for path in MILESTONE_SEQUENCE_PATHS:
        raw_groups = load_json(path)
        if not isinstance(raw_groups, list):
            raise ValueError(f"{path} must contain a list of milestone groups")  # noqa: TRY004

        for raw_group in raw_groups:
            if not isinstance(raw_group, list):
                raise ValueError(f"{path} must contain nested milestone lists")  # noqa: TRY004
            for raw_milestone in raw_group:
                if not isinstance(raw_milestone, str):
                    raise ValueError(f"{path} contains a non-string milestone")  # noqa: TRY004
                milestones.append(milestone_metadata_key(raw_milestone))

    return list(dict.fromkeys(milestones))


def check_img_url(milestone: str, img_url: str) -> str | None:
    """Checks if specified img url exists by sending a request.

    Args:
        milestone: Milestone name.
        img_url: Corresponding img url to milestone.
    Returns:
        None if img url exists, otherwise milestone name.
    """
    try:
        response = wiki_session.head(img_url, allow_redirects=True, timeout=TIMEOUT)
    except requests.RequestException as exc:
        return f"{milestone}: request failed for {img_url}: {exc}"

    if response.status_code == 429:
        return f"{milestone}: rate limited checking {img_url}"
    if response.status_code >= 400:
        return f"{milestone}: {img_url} returned HTTP {response.status_code}"
    return None


def check_metadata_img_urls() -> list[str]:
    """Check validity of all img urls corresponding to chart milestones in the metadata set."""
    metadata = load_milestone_metadata()
    milestones = load_milestones()
    missing_milestones = [
        milestone for milestone in milestones if milestone not in metadata
    ]
    if missing_milestones:
        raise ValueError(
            f"sequence milestone(s) missing from metadata: {missing_milestones}"
        )
    failures = []
    checkable_metadata = metadata

    checkable_metadata = {milestone: metadata[milestone] for milestone in milestones}

    for milestone, record in checkable_metadata.items():
        failure = check_img_url(milestone, str(record.imgUrl))
        if failure is not None:
            failures.append(failure)
    return failures


def main() -> int:
    try:
        failures = check_metadata_img_urls()
    except ValueError as exc:
        print(f"healthcheck failed: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("Invalid milestone metadata image URL(s):", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"OK: all milestone metadata image URLs are reachable in {METADATA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
