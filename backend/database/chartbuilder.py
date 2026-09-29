"""Chartbuilder share saving and loading."""

import json
from pathlib import Path

from backend.database.shared import get_pool


async def save_share(
    token: str,
    milestone_sequence: list[list[str]],
) -> None:
    """Add chartbuilder-save record to shares table.

    Args:
        token: chartbuilder token to insert with user submitted ms-sequence.
        milestone_sequence: User submitted ms-sequence.
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

    Args:
        token: Chartbuilder token corresponding to ms-sequence to be returned.

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


async def lookup_asset(milestone: str) -> tuple[bool, Path | None]:
    """Fetch milestone asset path from chartbuilder assets table if exists.

    Also logs lookup in chartbuilder asset lookups table.

    Args:
        milestone: Milestone to get path for.

    Returns:
        True if record exists, and asset path if exists or None.
    """
    lower = milestone.lower()
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO chartbuilder_asset_lookups
        (milestone, milestone_lowercase)
        VALUES($1, $2)
        """,
        milestone,
        lower,
    )
    row = await pool.fetchrow(
        """
        SELECT asset_path FROM chartbuilder_assets
        WHERE milestone_lowercase = $1
        """,
        lower,
    )
    record_exists = row is not None
    path = None
    if record_exists and row["asset_path"] is not None:
        path = Path(row["asset_path"])
    return record_exists, path


async def insert_asset(milestone: str, path: Path | None) -> None:
    """Add chartbuilder asset record.

    Null path implies improper milestone.

    Args:
        milestone: Canonical and valid milestone name.
        path: Milestone icon asset path.

    """
    lower = milestone.lower()
    pool = await get_pool()
    if path is None:
        await pool.execute(
            """
            INSERT INTO chartbuilder_assets
            (milestone_lowercase)
            VALUES ($1)
            """,
            lower,
        )
        return
    await pool.execute(
        """
        INSERT INTO chartbuilder_assets
        (milestone_lowercase, milestone_canonical, asset_path)
        VALUES ($1, $2, $3)
        """,
        lower,
        milestone,
        str(path),
    )
