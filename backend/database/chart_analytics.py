"""General fetch queries"""

import json
from datetime import datetime
from typing import Any, TypedDict

from backend.database.shared import get_pool, validate_milestone_completion_rate_window


class CompletionMetrics(TypedDict):
    """Metrics describing milestone completion."""

    completed_count: int
    total_count: int
    completion_rate: float | None  # None if total count is zero.


class SkipMetrics(TypedDict):
    """Metrics describing milestone skip."""

    skipped_count: int
    eligible_count: int
    skip_rate: float | None  # None if eligible count is zero.


def _snapshot_completed_set(snapshot: Any) -> set[str]:
    """Coerces ms-completed records into sets.

    Args:
        snapshot: ms-completed record to coerce.
    """
    if isinstance(snapshot, str):
        snapshot = json.loads(snapshot)
    return set(snapshot)


async def milestone_completion_rate(milestone_name: str) -> CompletionMetrics:
    """Get avg. completion rate for specified milestone.

    Args:
        milestone_name: Milestone to get completion rate for.

    Returns:
        completion count, total count, and completion rate.
    """
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT
            COUNT(*) AS total_count,
            COUNT(*) FILTER (
                WHERE milestones_completed ? $1
            ) AS completed_count
        FROM milestones_completed_snapshots
        """,
        milestone_name,
    )
    total_count = row["total_count"]
    completed_count = row["completed_count"]
    completion_rate = None
    if total_count:
        completion_rate = completed_count / total_count

    return {
        "completed_count": completed_count,
        "total_count": total_count,
        "completion_rate": completion_rate,
    }


async def milestone_completion_rates(
    milestone_names: list[str],
    start_time: datetime,
    stop_time: datetime,
) -> dict[str, CompletionMetrics]:
    """Get completion rate for specified milestones in specified time window.

    Args:
        milestone_names: Name of milestones to get fetch completion rates for
        start_time: Milestones after this datetime are included.
        stop_time: Milestones afte this datetime are excluded.

    Returns:
        ms-name:CompletionMetrics key-val pairs.
    """
    validate_milestone_completion_rate_window(start_time, stop_time)

    pool = await get_pool()
    rows = await pool.fetch(
        """
        WITH requested_milestones AS (
            SELECT DISTINCT unnest($1::text[]) AS milestone_name
        ),
        snapshots AS (
            SELECT id, milestones_completed
            FROM milestones_completed_snapshots
            WHERE created_at >= $2
                AND created_at < $3
        ),
        snapshot_count AS (
            SELECT COUNT(*) AS total_count
            FROM snapshots
        )
        SELECT
            requested_milestones.milestone_name,
            snapshot_count.total_count,
            COUNT(snapshots.id) FILTER (
                WHERE snapshots.milestones_completed
                    ? requested_milestones.milestone_name
            ) AS completed_count
        FROM requested_milestones
        CROSS JOIN snapshot_count
        LEFT JOIN snapshots ON true
        GROUP BY requested_milestones.milestone_name, snapshot_count.total_count
        """,
        milestone_names,
        start_time,
        stop_time,
    )

    completion_rates: dict[str, CompletionMetrics] = {}
    for row in rows:
        total_count = row["total_count"]
        completed_count = row["completed_count"]
        completion_rate = None
        if total_count:
            completion_rate = completed_count / total_count

        completion_rates[row["milestone_name"]] = {
            "completed_count": completed_count,
            "total_count": total_count,
            "completion_rate": completion_rate,
        }

    return completion_rates


async def milestone_skip_rate(
    milestone: str,
    subsequent_milestones: set[str],
    skip_threshold: int,
) -> SkipMetrics:
    """Retrieve SkipMetrics record for milestone in specified time interval.

    Args:
        milestone: Name of milestones to get fetch skip rates for
        subsequent_milestone: Milestones subsequent relative to milestone, but not in same group.

    Returns:
        SkipMetrics records keyed by corresponding milestone names.
    """
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        WITH snapshot_metrics AS (
            SELECT
                milestones_completed ? $1 AS completed_target,
                (
                    SELECT COUNT(*)
                    FROM jsonb_array_elements_text(milestones_completed) AS completed(name)
                    WHERE completed.name = ANY($2::text[])
                ) AS subsequent_completed_count
            FROM milestones_completed_snapshots
        )
        SELECT
            COUNT(*) FILTER (
                WHERE subsequent_completed_count >= $3
            ) AS eligible_count,
            COUNT(*) FILTER (
                WHERE subsequent_completed_count >= $3
                    AND NOT completed_target
            ) AS skipped_count
        FROM snapshot_metrics
        """,
        milestone,
        subsequent_milestones,
        skip_threshold,
    )
    eligible_count = row["eligible_count"]
    skipped_count = row["skipped_count"]
    skip_rate = None
    if eligible_count:
        skip_rate = skipped_count / eligible_count

    return {
        "skipped_count": skipped_count,
        "eligible_count": eligible_count,
        "skip_rate": skip_rate,
    }


async def fetch_completed_milestones_snapshots(
    start_time: datetime,
    stop_time: datetime,
) -> list[set[str]]:
    """Get completion rate for main-chart milestones in specified time window and infer skip rates.

    Args:
        start_time: Milestones after this datetime are included.
        stop_time: Milestones afte this datetime are excluded.

    Returns:
        milestone_name:SkipMetrics key-val pairs.
    """
    validate_milestone_completion_rate_window(start_time, stop_time)
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT milestones_completed
        FROM milestones_completed_snapshots
        WHERE created_at >= $1
            AND created_at < $2
        """,
        start_time,
        stop_time,
    )
    completed_milestones_snapshots = [
        _snapshot_completed_set(row["milestones_completed"]) for row in rows
    ]
    return completed_milestones_snapshots


async def get_visit_count(
    start_time: datetime,
    stop_time: datetime,
) -> int:
    """Return the number of visits within the last num_days.

    Args:
        start_time: Milestones after this datetime are included.
        stop_time: Milestones afte this datetime are excluded.

    Returns:
        Number of completed snapshots
    """
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT count(*)
        FROM milestones_completed_snapshots
        WHERE created_at >= $1
            AND created_at < $2
        """,
        start_time,
        stop_time,
    )
    return row["count"]


async def n_milestones_completed_count(num_days: int, ms_complete_count: int) -> int:
    """Get ms-completed record count where ms-complete count >= num_milestones.

    Args:
        num_days: Amount of days backwards to include records from.
        num_milestones: Lower cutoff for including records.

    Returns:
        Number of ms-completed records where ms-complete count >= num_milestones.
    """
    pool = await get_pool()
    count = await pool.fetchval(
        """
        SELECT count(*) AS count FROM milestones_completed_snapshots
        WHERE created_at >= now() - $1 * interval '1 day'
        AND jsonb_array_length(milestones_completed) >= $2
        """,
        num_days,
        ms_complete_count,
    )
    return count
