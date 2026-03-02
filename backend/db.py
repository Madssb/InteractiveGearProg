import json
import os
import re

import asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set")
SHARES_TABLE = os.getenv("SHARES_TABLE", "shares")
ENDPOINT_HITS_TABLE = os.getenv("ENDPOINT_HITS_TABLE", "endpoint_hits_daily")
TABLE_NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
if not TABLE_NAME_RE.match(SHARES_TABLE):
    raise SystemExit(
        "SHARES_TABLE must match ^[a-z_][a-z0-9_]*$ (example: shares or shares_test)"
    )
if not TABLE_NAME_RE.match(ENDPOINT_HITS_TABLE):
    raise SystemExit(
        "ENDPOINT_HITS_TABLE must match ^[a-z_][a-z0-9_]*$ "
        "(example: endpoint_hits_daily)"
    )


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
        f"""
        INSERT INTO {SHARES_TABLE} (token, sequence, items)
        VALUES ($1, $2, $3)
        """,
        token,
        json.dumps(sequence),
        json.dumps(items),
    )


async def load_share(token: str):
    pool = await get_pool()
    row = await pool.fetchrow(
        f"SELECT sequence, items FROM {SHARES_TABLE} WHERE token = $1", token
    )
    if row is None:
        return None
    return json.loads(row["sequence"]), json.loads(row["items"])


async def increment_endpoint_hit(endpoint: str) -> None:
    pool = await get_pool()
    await pool.execute(
        f"""
        INSERT INTO {ENDPOINT_HITS_TABLE} (day, endpoint, hits)
        VALUES (CURRENT_DATE, $1, 1)
        ON CONFLICT (day, endpoint)
        DO UPDATE SET hits = {ENDPOINT_HITS_TABLE}.hits + 1
        """,
        endpoint,
    )
