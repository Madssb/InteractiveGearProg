import os
from datetime import datetime, timezone

import asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set")


_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Instantiate pool

    Returns:
        Single global connection pool shared by all db ops.
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool


def validate_milestone_completion_rate_window(
    start_time: datetime,
    stop_time: datetime,
) -> None:
    """Ensure start_time and stop_time behave appropriately.

    Args:
        start_time: Milestones after this datetime are included.
        stop_time: Milestones afte this datetime are excluded.
    """
    if start_time.tzinfo is None or start_time.utcoffset() is None:
        raise ValueError("start_time must include timezone information")

    if stop_time.tzinfo is None or stop_time.utcoffset() is None:
        raise ValueError("stop_time must include timezone information")

    if start_time >= stop_time:
        raise ValueError("start_time must be before stop_time")

    if stop_time > datetime.now(timezone.utc):
        raise ValueError("stop_time cannot be in the future")
