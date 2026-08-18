"""PostgreSQL statements for ladlorchart api backend and botlor"""

import json
import os
from datetime import date, datetime, timezone
from functools import cache
from typing import Any, Literal, TypedDict

import asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set")


_pool: asyncpg.Pool | None = None


class MilestoneAnnotationRow(TypedDict):
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


class AnnotationOwnerAndMessageIds(TypedDict):
    user_id: int
    message_id: int


class ResolvedReport(TypedDict):
    report_type: Literal["annotation", "user"]
    report_id: int


class ResolveReportResult(TypedDict):
    status: Literal["resolved", "not_found", "ambiguous"]
    resolved_report: ResolvedReport | None


class UnresolvedReport(TypedDict):
    report_type: Literal["annotation", "user"]
    report_id: int


class MilestoneCompletionRate(TypedDict):
    completed_count: int
    total_count: int
    completion_rate: float | None


class MilestoneSkipRate(TypedDict):
    skipped_count: int
    eligible_count: int
    skip_rate: float | None


class MilestoneAnnotationViewCount(TypedDict):
    view_count: int


class MilestoneAnnotationStatus(TypedDict):
    has_annotation: bool


def validate_milestone_completion_rate_window(
    start_time: datetime,
    stop_time: datetime,
) -> None:
    if start_time.tzinfo is None or start_time.utcoffset() is None:
        raise ValueError("start_time must include timezone information")

    if stop_time.tzinfo is None or stop_time.utcoffset() is None:
        raise ValueError("stop_time must include timezone information")

    if start_time >= stop_time:
        raise ValueError("start_time must be before stop_time")

    if stop_time > datetime.now(timezone.utc):
        raise ValueError("stop_time cannot be in the future")


async def next_report_id(connection: asyncpg.Connection) -> int:
    await connection.execute("SELECT pg_advisory_xact_lock(1506719382213099610)")
    report_id = await connection.fetchval(
        """
        SELECT COALESCE(MAX(report_id), 0) + 1
        FROM (
            SELECT report_id FROM annotation_reports
            UNION ALL
            SELECT report_id FROM user_reports
        ) AS report_ids
        """
    )
    return report_id


@cache
def latest_chart_version() -> str:
    changelog_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "contents",
        "changelog.json",
    )
    with open(changelog_path, encoding="utf-8") as changelog:
        return next(iter(json.load(changelog)))


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool


async def save_share(
    token: str,
    milestone_sequence: list[list[str]],
) -> None:
    """Add chartbuilder-save record to shares table"""
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO shares (token, milestone_sequence)
        VALUES ($1, $2)
        """,
        token,
        json.dumps(milestone_sequence),
    )


async def load_share(token: str) -> list[list[str]] | None:
    """Retrieve chartbuilder-save record from shares table

    Args:
        token: Chartbuilder-token.

    Returns:
        Milestone sequence if exists or None.
    """
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT milestone_sequence FROM shares
        WHERE token = $1
        """,
        token,
    )
    if row is None:
        return None
    return json.loads(row["milestone_sequence"])


async def update_endpoint_hits(endpoint: str) -> None:
    """Add endpoint call record to endpoint_hits table

    Args:
        Name of the endpoint hit.
    """
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO endpoint_hits (endpoint)
        VALUES ($1)
        """,
        endpoint,
    )


async def milestones_completed_snapshots(milestones_completed: list[str]) -> None:
    """Add completed-milestones record to milestones_completed_snapshots table.

    Args:
        milestones_completed: Milestones completed by user.
    """
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO milestones_completed_snapshots (milestones_completed)
        VALUES ($1)
        """,
        json.dumps(milestones_completed),
    )


async def milestones_hidden_snapshots(milestones_hidden: list[str]) -> None:
    """Add hidden-milestones record to milestones_hidden_snapshots table.

    Args:
        milestones_hidden: Milestones hidden by user.
    """
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO milestones_hidden_snapshots (milestones_hidden)
        VALUES ($1)
        """,
        json.dumps(milestones_hidden),
    )


async def annotation_view_event(milestone_name: str) -> None:
    """Add annotation panel view record.

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


async def milestone_completion_rate(milestone_name: str) -> MilestoneCompletionRate:
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
) -> dict[str, MilestoneCompletionRate]:
    """Retrieve MilestoneCompletionRate records for specified milestones in specified datetime period.

    Args:
        milestone_names: Name of milestones to get fetch completion rates for
        start_time: Milestones after this datetime are included.
        stop_time: Milestones afte this datetime are excluded.

    Returns:
        MilestoneCompletionRate records keyed by corresponding milestone names.
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

    completion_rates: dict[str, MilestoneCompletionRate] = {}
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


def _snapshot_completed_set(snapshot: Any) -> set[str]:
    if isinstance(snapshot, str):
        snapshot = json.loads(snapshot)
    return set(snapshot)


def _has_skip_eligible_progress(
    completed_milestones: set[str],
    subsequent_milestone_names: list[str],
    skip_threshold: int,
) -> bool:
    subsequent_completed_count = 0
    for milestone_name in subsequent_milestone_names:
        if milestone_name not in completed_milestones:
            continue
        subsequent_completed_count += 1
        if subsequent_completed_count >= skip_threshold:
            return True
    return False


async def milestone_skip_rates(
    milestone_contexts: dict[str, tuple[list[str], int]],
    start_time: datetime,
    stop_time: datetime,
) -> dict[str, MilestoneSkipRate]:
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
    snapshot_sets = [
        _snapshot_completed_set(row["milestones_completed"]) for row in rows
    ]

    skip_rates: dict[str, MilestoneSkipRate] = {}
    for milestone_name, (
        subsequent_milestone_names,
        threshold,
    ) in milestone_contexts.items():
        eligible_count = 0
        skipped_count = 0
        for completed_milestones in snapshot_sets:
            if not _has_skip_eligible_progress(
                completed_milestones,
                subsequent_milestone_names,
                threshold,
            ):
                continue
            eligible_count += 1
            if milestone_name not in completed_milestones:
                skipped_count += 1

        skip_rate = None
        if eligible_count:
            skip_rate = skipped_count / eligible_count

        skip_rates[milestone_name] = {
            "skipped_count": skipped_count,
            "eligible_count": eligible_count,
            "skip_rate": skip_rate,
        }

    return skip_rates


async def milestone_annotation_view_counts(
    milestone_names: list[str],
    start_time: datetime,
    stop_time: datetime,
) -> dict[str, MilestoneAnnotationViewCount]:
    validate_milestone_completion_rate_window(start_time, stop_time)

    pool = await get_pool()
    rows = await pool.fetch(
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
        milestone_names,
        start_time,
        stop_time,
    )
    return {row["milestone_name"]: {"view_count": row["view_count"]} for row in rows}


async def milestone_annotation_statuses(
    milestones_by_name: dict[str, int],
) -> dict[str, MilestoneAnnotationStatus]:
    pool = await get_pool()
    rows = await pool.fetch(
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
            ) AS has_annotation
        FROM requested_milestones
        """,
        json.dumps(milestones_by_name),
    )
    return {
        row["milestone_name"]: {"has_annotation": row["has_annotation"]} for row in rows
    }


async def milestone_skip_rate(
    milestone_name: str,
    subsequent_milestone_names: list[str],
    skip_threshold: int,
) -> MilestoneSkipRate:
    """Retrieve MilestoneSkipRate records for specified milestones in specified datetime period.

    Args:
        milestone_names: Name of milestones to get fetch skip rates for
        start_time: Milestones after this datetime are included.
        stop_time: Milestones afte this datetime are excluded.

    Returns:
        MilestoneSkipRate records keyed by corresponding milestone names.
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
        milestone_name,
        subsequent_milestone_names,
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


async def annotation_submission(
    message_id: int,
    milestone_id: int,
    user_id: int,
    user_display_name: str,
    annotation_text: str,
) -> int:
    """
    Handle annotation submission.
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


async def annotation_vote(
    message_id: int,
    up_count: int,
    down_count: int,
) -> None:
    """Register annotation vote"""
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


async def annotation_report(
    annotation_id: int,
    reporter_user_id: int,
    reason: str,
) -> int:
    pool = await get_pool()
    async with pool.acquire() as connection, connection.transaction():
        report_id = await next_report_id(connection)
        await connection.execute(
            """
                INSERT INTO annotation_reports (
                    report_id,
                    annotation_id,
                    reporter_user_id,
                    reason
                )
                OVERRIDING SYSTEM VALUE
                VALUES ($1, $2, $3, $4)
                """,
            report_id,
            annotation_id,
            reporter_user_id,
            reason,
        )
        return report_id


async def user_report(
    reported_name: str,
    reporter_user_id: int,
    reason: str,
) -> int:
    pool = await get_pool()
    async with pool.acquire() as connection, connection.transaction():
        report_id = await next_report_id(connection)
        await connection.execute(
            """
                INSERT INTO user_reports (
                    report_id,
                    reported_name,
                    reporter_user_id,
                    reason
                )
                OVERRIDING SYSTEM VALUE
                VALUES ($1, $2, $3, $4)
                """,
            report_id,
            reported_name,
            reporter_user_id,
            reason,
        )
        return report_id


async def resolve_report(report_id: int, verdict: str) -> ResolveReportResult:
    pool = await get_pool()
    async with pool.acquire() as connection, connection.transaction():
        annotation_report_id = await connection.fetchval(
            """
                SELECT report_id
                FROM annotation_reports
                WHERE report_id = $1
                    AND ongoing = true
                FOR UPDATE
                """,
            report_id,
        )
        user_report_id = await connection.fetchval(
            """
                SELECT report_id
                FROM user_reports
                WHERE report_id = $1
                    AND ongoing = true
                FOR UPDATE
                """,
            report_id,
        )

        matches = [
            ("annotation", annotation_report_id),
            ("user", user_report_id),
        ]
        matches = [
            (report_type, matched_id)
            for report_type, matched_id in matches
            if matched_id is not None
        ]

        if not matches:
            return {"status": "not_found", "resolved_report": None}

        if len(matches) > 1:
            return {"status": "ambiguous", "resolved_report": None}

        report_type, matched_id = matches[0]
        table_name = (
            "annotation_reports" if report_type == "annotation" else "user_reports"
        )
        await connection.execute(
            f"""
                UPDATE {table_name}
                SET ongoing = false,
                    verdict = $1,
                    resolved_at = now()
                WHERE report_id = $2
                """,
            verdict,
            matched_id,
        )
        return {
            "status": "resolved",
            "resolved_report": {
                "report_type": report_type,
                "report_id": matched_id,
            },
        }


async def unresolved_reports() -> list[UnresolvedReport]:
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT 'annotation' AS report_type, report_id
        FROM annotation_reports
        WHERE ongoing = true

        UNION ALL

        SELECT 'user' AS report_type, report_id
        FROM user_reports
        WHERE ongoing = true

        ORDER BY report_id
        """
    )
    return [dict(row) for row in rows]


async def milestone_annotations_lookup(
    milestone_id: int,
) -> list[MilestoneAnnotationRow]:
    """
    Fetch annotations for milestones, exclude annotations with ongoing reports.
    """
    pool = await get_pool()
    rows = await pool.fetch(
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
    return [dict(row) for row in rows]


async def milestone_annotation_message_lookup(
    milestone_id: int,
) -> list[MilestoneAnnotationMessageRow]:
    """
    Fetch annotation Discord message IDs for a milestone, excluding ongoing reports.
    """
    pool = await get_pool()
    rows = await pool.fetch(
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
    return [dict(row) for row in rows]


async def annotated_milestone_ids() -> set[int]:
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT DISTINCT milestone_id
        FROM annotations
        """
    )
    return {row["milestone_id"] for row in rows}


async def get_annotation_owner_and_message_ids(
    annotation_id: int,
) -> AnnotationOwnerAndMessageIds | None:
    """Fetch Discord user and message IDs for an annotation."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT user_id, message_id
        FROM annotations
        WHERE annotation_id = $1
        """,
        annotation_id,
    )
    if row is None:
        return None
    return dict(row)


async def remove_annotation_record(annotation_id: int) -> bool:
    pool = await get_pool()
    status = await pool.execute(
        """
        DELETE FROM annotations
        WHERE annotation_id = $1
        """,
        annotation_id,
    )
    return status == "DELETE 1"
