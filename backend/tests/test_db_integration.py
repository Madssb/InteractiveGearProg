import asyncio
import os

import asyncpg
import pytest

_DUMMY_TEST_DB_URL = "postgresql://user:password@localhost:5432/testdb?sslmode=disable"


@pytest.mark.db
def test_database_connectivity_smoke():
    """DB smoke check: verify DATABASE_URL accepts a connection and SELECT 1 succeeds."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url or database_url == _DUMMY_TEST_DB_URL:
        pytest.skip("Set a real DATABASE_URL to run db-marked integration checks.")

    async def _check():
        conn = await asyncpg.connect(database_url, timeout=5)
        try:
            return await conn.fetchval("SELECT 1")
        finally:
            await conn.close()
    assert asyncio.run(asyncio.wait_for(_check(), timeout=12)) == 1


@pytest.mark.db
def test_schema_matches_expected_shares_contract():
    """Schema contract check for public.shares columns/types and primary key shape."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url or database_url == _DUMMY_TEST_DB_URL:
        pytest.skip("Set a real DATABASE_URL to run db-marked integration checks.")
    shares_table = os.getenv("SHARES_TABLE", "shares")

    async def _check_schema():
        conn = await asyncpg.connect(database_url, timeout=5)
        try:
            table_exists = await conn.fetchval(
                """
                SELECT EXISTS (
                  SELECT 1
                  FROM information_schema.tables
                  WHERE table_schema = 'public' AND table_name = $1
                )
                """,
                shares_table,
            )
            if not table_exists:
                return {"table_exists": False}

            cols = await conn.fetch(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = $1
                ORDER BY ordinal_position
                """,
                shares_table,
            )
            pk_cols = await conn.fetch(
                """
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                WHERE tc.table_schema = 'public'
                  AND tc.table_name = $1
                  AND tc.constraint_type = 'PRIMARY KEY'
                ORDER BY kcu.ordinal_position
                """,
                shares_table,
            )
            return {
                "table_exists": True,
                "columns": {row["column_name"]: row["data_type"] for row in cols},
                "pk_cols": [row["column_name"] for row in pk_cols],
            }
        finally:
            await conn.close()

    result = asyncio.run(asyncio.wait_for(_check_schema(), timeout=20))
    assert result["table_exists"] is True, f"Expected public.{shares_table} table to exist."
    assert result["columns"] == {
        "token": "text",
        "sequence": "jsonb",
        "items": "jsonb",
    }
    assert result["pk_cols"] == ["token"]
