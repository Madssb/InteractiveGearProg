"""This is for things i havent decided where they go."""

from backend.database.shared import get_pool


async def update_endpoint_hits(endpoint: str) -> None:
    """Add endpoint call record to endpoint_hits table.

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
