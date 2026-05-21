"""
Milestone to id lookup and vice versa
"""
import json
from functools import cache
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MILESTONE_IDS_PATH = REPO_ROOT / "data/logic/milestone-ids.json"


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
