"""
Milestone to id lookup and vice versa
"""
import json
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
        [
            milestone.removeprefix("*")
            for milestone in group
        ]
        for group in raw_groups
    ]
