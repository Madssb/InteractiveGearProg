import json
import os
from functools import cache

import asyncpg
from dotenv import load_dotenv
from datetime import date
from typing import TypedDict


class MilestoneAnnotationRow(TypedDict):
    annotation_id: int
    up_count: int
    down_count: int
    chart_version: str
    annotation_text: str
    created_at: date

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set")

_pool: asyncpg.Pool | None = None


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
    token: str, milestone_sequence: list[list[str]],
) -> None:
    """Add chartbuilder-save record to shares table
    """
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
    """
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT milestone_sequence FROM shares
        WHERE token = $1
        """,
        token
    )
    if row is None:
        return None
    return json.loads(row["milestone_sequence"])


async def update_endpoint_hits(endpoint: str) -> None:
    """Add endpoint call record to endpoint_hits table
    """
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO endpoint_hits (endpoint)
        VALUES ($1)
        """,
        endpoint
    )


async def milestones_completed_snapshots(milestones_completed: list[str]):
    """Add completed-milestones record to milestones_completed_snapshots table.
    """
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO milestones_completed_snapshots (milestones_completed)
        VALUES ($1)
        """,
        json.dumps(milestones_completed)
    )


async def milestones_hidden_snapshots(milestones_hidden: list[str]):
    """Add hidden-milestones record to milestones_hidden_snapshots table."""
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO milestones_hidden_snapshots (milestones_hidden)
        VALUES ($1)
        """,
        json.dumps(milestones_hidden)
    )


async def annotation_submission(
    message_id: int,
    milestone_id: int,
    user_id: int,
    annotation_text: str
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
            milestone_id, user_id,
            chart_version,
            annotation_text
        )
        VALUES($1, $2, $3, $4, $5) 
        RETURNING annotation_id
        """,
        message_id,
        milestone_id,
        user_id,
        chart_version,
        annotation_text
    )
    return annotation_id

async def annotation_vote(
    message_id: int,
    up_count: int,
    down_count: int,
) -> None:
    """Register annotation vote
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
        message_id
    )

async def annotation_report(
    annotation_id: int,
    reporter_user_id: int,
    reason: str,
) -> None:
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO annotation_reports (
            annotation_id,
            reporter_user_id,
            reason
        )
        VALUES ($1, $2, $3)
        """,
        annotation_id,
        reporter_user_id,
        reason,
    )

async def milestone_annotations_lookup(milestone_id: int) -> list[MilestoneAnnotationRow]:
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
            a.created_at::date AS created_at
        FROM annotations AS a
        WHERE a.milestone_id = $1
        AND NOT EXISTS (
            SELECT 1
            FROM annotation_reports AS r
            WHERE r.annotation_id = a.annotation_id
                AND r.ongoing = true
        )
        """,
        milestone_id,
    )
    return [dict(row) for row in rows]
