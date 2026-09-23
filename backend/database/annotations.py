"""SQL Statements for annotation management"""

import json
from datetime import date, datetime
from functools import cache
from itertools import chain
from pathlib import Path
from typing import TypedDict

from backend.database.shared import get_pool, validate_milestone_completion_rate_window
from backend.milestones import load_main_milestone_groups, load_milestone_ids_by_name

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MILESTONE_IDS_BY_NAME = load_milestone_ids_by_name()

MAIN_SEQUENCE_GROUPS = load_main_milestone_groups()
MAIN_SEQUENCE_FLAT = list(chain.from_iterable(MAIN_SEQUENCE_GROUPS))


class MilestoneAnnotationStatus(TypedDict):
    is_visible: bool


class AnnotationOwnerAndMessageIds(TypedDict):
    user_id: int
    message_id: int


class AnnotationRecord(TypedDict):
    annotation_id: int
    up_count: int
    down_count: int
    chart_version: str
    annotation_text: str
    user_display_name: str
    created_at: date


class MilestoneAnnotationMessageRow(TypedDict):
    annotation_id: int
    message_id: int


@cache
def latest_chart_version() -> str:
    """Get latest chart version from changelog."""
    changelog_path = ROOT_DIR / "data/contents/changelog.json"
    with open(changelog_path, encoding="utf-8") as changelog:
        return next(iter(json.load(changelog)))


async def annotation_submission(
    message_id: int,
    milestone_id: int,
    user_id: int,
    user_display_name: str,
    annotation_text: str,
) -> int:
    """Add annotation record.

    Args:
        message_id (int): ID of output discord message by bot for annotation.
        milestone_id (int): ID of annotated milestone.
        user_id (int): Discord user ID.
        user_display_name (str): Display name at submission time.
        annotation_text (str): User submitted annotation text.

    Returns:
        Annotation ID.
    """
    pool = await get_pool()
    chart_version = latest_chart_version()
    annotation_id = await pool.fetchval(
        """
        INSERT INTO annotations (
            message_id,
            milestone_id,
            user_id,
            user_display_name,
            chart_version,
            annotation_text
        )
        VALUES($1, $2, $3, $4, $5, $6)
        RETURNING annotation_id
        """,
        message_id,
        milestone_id,
        user_id,
        user_display_name,
        chart_version,
        annotation_text,
    )
    return annotation_id


async def remove_annotation_record(annotation_id: int) -> bool:
    """Delete annotation record.

    Args:
        milestone_id (int): ID of annotated milestone.

    Returns:
        True if successfully deleted.
    """
    pool = await get_pool()
    status = await pool.execute(
        """
        DELETE FROM annotations
        WHERE annotation_id = $1
        """,
        annotation_id,
    )
    return status == "DELETE 1"


async def annotation_view_event(milestone_name: str) -> None:
    """Add annotation view record.

    Args:
        milestone_name: Name of milestone with annotation view event.
    """
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO annotation_view_event (milestone_name)
        VALUES ($1)
        """,
        milestone_name,
    )


async def annotation_vote(
    message_id: int,
    up_count: int,
    down_count: int,
) -> None:
    """Register annotation vote.

    Args:
        message_id (int): ID of output discord message by bot for annotation.
        up_count (int): Number of thumbs up reactions on message.
        down_count (int): Number of thumbs down reactions on message.
    """
    pool = await get_pool()
    await pool.execute(
        """
        UPDATE annotations
        SET up_count = $1, down_count = $2
        WHERE message_id = $3
        """,
        up_count,
        down_count,
        message_id,
    )


async def milestone_annotation_view_counts(
    start_time: datetime,
    stop_time: datetime,
) -> dict[str, int]:
    """Fetch annotation view counts for the main-sequence milestones.

    Args:
        start_time: Cut records from before this datetime.
        stop_time: Cut records from after this datetime.

    Returns:
        Milestone-name:annotation-view-count key-val pairs.
    """
    validate_milestone_completion_rate_window(start_time, stop_time)

    pool = await get_pool()
    records = await pool.fetch(
        """
        WITH requested_milestones AS (
            SELECT DISTINCT unnest($1::text[]) AS milestone_name
        )
        SELECT
            requested_milestones.milestone_name,
            COUNT(annotation_view_event.id) AS view_count
        FROM requested_milestones
        LEFT JOIN annotation_view_event
            ON annotation_view_event.milestone_name = requested_milestones.milestone_name
            AND annotation_view_event.created_at >= $2
            AND annotation_view_event.created_at < $3
        GROUP BY requested_milestones.milestone_name
        """,
        MAIN_SEQUENCE_FLAT,
        start_time,
        stop_time,
    )
    return {record["milestone_name"]: record["view_count"] for record in records}


async def fetch_annotation_visibility_statuses() -> set[str]:
    """Fetch chart milestones with one or more visible annotations.

    A milestone annotation is visible if it doesn't have an ongoing report.

    Returns:
        Milestones with one or more visible annotations.
    """
    pool = await get_pool()
    records = await pool.fetch(
        """
        WITH requested_milestones AS (
            SELECT *
            FROM jsonb_each_text($1::jsonb)
        )
        SELECT
            requested_milestones.key AS milestone_name,
            EXISTS (
                SELECT 1
                FROM annotations AS a
                WHERE a.milestone_id = requested_milestones.value::integer
                    AND NOT EXISTS (
                        SELECT 1
                        FROM annotation_reports AS r
                        WHERE r.annotation_id = a.annotation_id
                            AND r.ongoing = true
                    )
            ) AS is_visible
        FROM requested_milestones
        """,
        json.dumps(MILESTONE_IDS_BY_NAME),
    )
    visible_milestones = set({})
    for record in records:
        if record["is_visible"]:
            visible_milestones.add(record["milestone_name"])
    return visible_milestones


async def get_annotation_owner_and_message_ids(
    annotation_id: int,
) -> AnnotationOwnerAndMessageIds | None:
    """Fetch discord ids for annotation id.

    Args:
        annotation_id: milestone annotation id.
    """
    pool = await get_pool()
    record = await pool.fetchrow(
        """
        SELECT user_id, message_id
        FROM annotations
        WHERE annotation_id = $1
        """,
        annotation_id,
    )
    if record is None:
        return None
    return {"user_id": record["user_id"], "message_id": record["message_id"]}


async def annotated_milestone_ids() -> set[int]:
    """Fetch Milestone IDs for annotated milestones.

    Returns:
        Set of milestone IDs for annotated milestones.
    """
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT DISTINCT milestone_id
        FROM annotations
        """
    )
    return {record["milestone_id"] for record in records}


async def milestone_annotations_lookup(
    milestone_id: int,
) -> list[AnnotationRecord]:
    """
    Fetch annotation for milestone.

    Exclude annotations with ongoing reports.

    Args:
        milestone_id: Chart milestone ID to do lookup for.

    Returns:
        Annotation records.
    """
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT
            a.annotation_id,
            a.up_count,
            a.down_count,
            a.chart_version,
            a.annotation_text,
            a.user_display_name,
            a.created_at::date AS created_at
        FROM annotations AS a
        WHERE a.milestone_id = $1
        AND NOT EXISTS (
            SELECT 1
            FROM annotation_reports AS r
            WHERE r.annotation_id = a.annotation_id
                AND r.ongoing = true
        )
        ORDER BY (a.up_count - a.down_count) DESC, a.up_count DESC, a.created_at ASC
        """,
        milestone_id,
    )
    return [
        {
            "annotation_id": record["annotation_id"],
            "up_count": record["up_count"],
            "down_count": record["down_count"],
            "chart_version": record["chart_version"],
            "annotation_text": record["annotation_text"],
            "user_display_name": record["user_display_name"],
            "created_at": record["created_at"],
        }
        for record in records
    ]


async def milestone_annotation_message_lookup(
    milestone_id: int,
) -> list[MilestoneAnnotationMessageRow]:
    """Fetch annotation Discord message IDs for a milestone, excluding ongoing reports.

    Args:
        milestone_id: Chart infra provisioned milestone ID.

    Returns:
        Annotation ID + message ID records.
    """
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT a.annotation_id, a.message_id
        FROM annotations AS a
        WHERE a.milestone_id = $1
        AND a.message_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1
            FROM annotation_reports AS r
            WHERE r.annotation_id = a.annotation_id
                AND r.ongoing = true
        )
        ORDER BY (a.up_count - a.down_count) DESC, a.up_count DESC, a.created_at ASC
        """,
        milestone_id,
    )
    return [
        {
            "annotation_id": record["annotation_id"],
            "message_id": record["message_id"],
        }
        for record in records
    ]
