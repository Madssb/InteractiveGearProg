import json
import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set")

_pool: asyncpg.Pool | None = None


async def get_pool():
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
