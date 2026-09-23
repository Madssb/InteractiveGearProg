"""Add snapshot records"""

import json

from backend.database.shared import get_pool


async def record_completed_milestones_snapshot(milestones_completed: list[str]) -> None:
    """Add set-of-completed-milestones record to milestones_completed_snapshots table.

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


async def record_hidden_milestones_snapshot(milestones_hidden: set[str]) -> None:
    """Add set-of-hidden-milestones record to milestones_hidden_snapshots table.

    Args:
        milestones_hidden: Milestones hidden by user.
    """
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO milestones_hidden_snapshots (milestones_hidden)
        VALUES ($1)
        """,
        json.dumps(list(milestones_hidden)),
    )
