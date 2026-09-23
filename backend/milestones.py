"""
Milestone:Id lookup, ID:Milestone lookup, and skip rate fetch and compute.
"""

import json
import math
from datetime import datetime
from functools import cache
from itertools import chain
from pathlib import Path

from backend.database.chart_analytics import (
    SkipMetrics,
    fetch_completed_milestones_snapshots,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MILESTONE_IDS_PATH = REPO_ROOT / "data/logic/milestone-ids.json"
MILESTONE_SEQUENCE_MAIN_PATH = REPO_ROOT / "data/logic/milestone-sequence-main.json"


@cache
def load_milestone_names_by_id() -> dict[int, str]:
    """Get ms-id:ms-name key-val pairs."""
    with MILESTONE_IDS_PATH.open("r", encoding="utf-8") as f:
        raw_milestone_ids = json.load(f)
    return {
        int(milestone_id): milestone
        for milestone_id, milestone in raw_milestone_ids.items()
    }


@cache
def load_milestone_ids_by_name() -> dict[str, int]:
    """Get ms-name:ms-id key-val pairs."""
    return {
        milestone: milestone_id
        for milestone_id, milestone in load_milestone_names_by_id().items()
    }


@cache
def load_main_milestone_groups() -> list[list[str]]:
    """Load grouping-aware main sequence."""
    with MILESTONE_SEQUENCE_MAIN_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_subsequent_milestones(milestone: str) -> set[str] | None:
    """Get subsequent milestones relative to specified milestone in main chart."""
    main_sequence_groups = load_main_milestone_groups()
    for idx, group in enumerate(main_sequence_groups):
        for milestone_ in group:
            if milestone_ != milestone:
                continue
            return set(chain.from_iterable(main_sequence_groups[idx + 1 :]))


def get_skip_threshold(subsequent_milestone_count: int) -> int:
    """Get adaptive skip threshold.

    if count of milestones in subsequent groups relative to some
    milestone exceed the threshold, milestone is skipped.

    Args:
        subsequent_milestone_count: Number of subsequent milestones.

    Returns:
        The count of milestones completed in subsequent groups relative
        to some milestone for which the milestone is considered skipped.
    """
    return math.floor(min(5, max(subsequent_milestone_count / 10, 1)))


def compute_skip_metrics(completed_milestones: set[str]) -> tuple[set[str], set[str]]:
    """Compute skip metrics for milestones completed snapshot.

    skip_eligibility means candidate ms has sufficiently high
    subsequent completed ms count to qualify as skipped if not
    also completed.

    Args:
        completed_milestones: Milestones completed snapshot.

    Returns:
        Skipped milestones and skip-eligible milestones.
    """
    main_sequence_groups = load_main_milestone_groups()
    skipped = set({})
    eligible = set({})
    for idx, group in enumerate(main_sequence_groups):
        # shared-group subseq-indexed milestones are not semantically subseq.
        subsequent_milestones = set(
            chain.from_iterable(main_sequence_groups[idx + 1 :])
        )
        subsequent_completed_milestones = subsequent_milestones | completed_milestones
        for milestone in group:
            eligible_ = len(subsequent_completed_milestones) > get_skip_threshold(
                len(subsequent_milestones)
            )
            if eligible_:
                eligible.add(milestone)
                if milestone not in completed_milestones:
                    skipped.add(milestone)
    return skipped, eligible


async def fetch_skip_metrics(
    start_time: datetime, stop_time: datetime
) -> dict[str, SkipMetrics]:
    """Fetch skip metrics for all main-chart milestones.

    Args:
        start_time:
        stop_time:
    Returns:
        Skip metrics for all main-chart milestones.
    """
    main_sequence_milestones = list(chain.from_iterable(load_main_milestone_groups()))
    completed_milestones_snapshots = await fetch_completed_milestones_snapshots(
        start_time, stop_time
    )

    skip_data: dict[str, SkipMetrics] = {}
    for snapshot in completed_milestones_snapshots:
        skipped, eligible = compute_skip_metrics(snapshot)
        for milestone in main_sequence_milestones:
            eligible_count = 0
            skipped_count = 0
            skip_rate = None
            if milestone in eligible:
                eligible_count += 1
                if milestone in skipped:
                    skipped_count += 1
            if eligible_count != 0:
                skip_rate = skipped_count / eligible_count
            skip_data[milestone] = {
                "eligible_count": eligible_count,
                "skipped_count": skipped_count,
                "skip_rate": skip_rate,
            }
    return skip_data
