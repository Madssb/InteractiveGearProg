"""
Milestone to id lookup and vice versa
"""

import json
import math
from functools import cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MILESTONE_IDS_PATH = REPO_ROOT / "data/logic/milestone-ids.json"
MILESTONE_SEQUENCE_MAIN_PATH = REPO_ROOT / "data/logic/milestone-sequence-main.json"


@cache
def load_milestone_names_by_id() -> dict[int, str]:
    with MILESTONE_IDS_PATH.open("r", encoding="utf-8") as f:
        raw_milestone_ids = json.load(f)
    return {
        int(milestone_id): milestone
        for milestone_id, milestone in raw_milestone_ids.items()
    }


@cache
def load_milestone_ids_by_name() -> dict[str, int]:
    return {
        milestone: milestone_id
        for milestone_id, milestone in load_milestone_names_by_id().items()
    }


@cache
def load_main_milestone_groups() -> list[list[str]]:
    with MILESTONE_SEQUENCE_MAIN_PATH.open("r", encoding="utf-8") as f:
        raw_groups = json.load(f)
    return [
        [milestone.removeprefix("*") for milestone in group] for group in raw_groups
    ]


def skip_threshold(remaining_milestone_count: int) -> int:
    return math.floor(min(5, max(remaining_milestone_count / 10, 1)))


def metric_name(milestone_name: str) -> str:
    parts = milestone_name.split(maxsplit=1)
    if len(parts) == 2 and parts[0].isdigit():
        return parts[1]
    return milestone_name


def milestone_context_from_groups(
    milestone_name: str,
    milestone_groups: list[list[str]],
) -> tuple[str, list[str]] | None:
    for group_index, group in enumerate(milestone_groups):
        for candidate_name in group:
            if milestone_name not in {candidate_name, metric_name(candidate_name)}:
                continue
            later_milestone_names = [
                later_milestone_name
                for later_group in milestone_groups[group_index + 1 :]
                for later_milestone_name in later_group
            ]
            return candidate_name, later_milestone_names
    return None
