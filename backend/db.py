import json
import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set")


async def get_pool():
    global _pool
    try:
        return _pool
    except NameError:
        _pool = await asyncpg.create_pool(DATABASE_URL)
        return _pool


async def save_share(
    token: str, sequence: list[list[str]], items: dict[str, dict[str, str]]
) -> None:
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO shares (token, sequence, items)
        VALUES ($1, $2, $3)
        """,
        token,
        json.dumps(sequence),
        json.dumps(items),
    )


async def load_share(token: str):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT sequence, items FROM shares WHERE token = $1", token
    )
    if row is None:
        return None
    return json.loads(row["sequence"]), json.loads(row["items"])
