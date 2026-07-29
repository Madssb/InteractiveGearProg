import asyncio
from datetime import UTC, datetime, timedelta

import pytest

import db


class FakePool:
    def __init__(self, rows):
        self.rows = rows
        self.milestone_names = None
        self.start_time = None
        self.stop_time = None

    async def fetch(self, _query, milestone_names, start_time, stop_time):
        self.milestone_names = milestone_names
        self.start_time = start_time
        self.stop_time = stop_time
        return self.rows


def test_milestone_completion_rates_returns_rates_by_milestone(monkeypatch):
    rows = [
        {
            "milestone_name": "Dragon scimitar",
            "total_count": 4,
            "completed_count": 3,
        },
        {
            "milestone_name": "Barrows gloves",
            "total_count": 4,
            "completed_count": 1,
        },
    ]
    pool = FakePool(rows)

    async def fake_get_pool():
        return pool

    monkeypatch.setattr(db, "get_pool", fake_get_pool)
    start_time = datetime(2026, 1, 1, tzinfo=UTC)
    stop_time = datetime(2026, 2, 1, tzinfo=UTC)

    result = asyncio.run(
        db.milestone_completion_rates(
            ["Dragon scimitar", "Barrows gloves"],
            start_time,
            stop_time,
        )
    )

    assert pool.milestone_names == ["Dragon scimitar", "Barrows gloves"]
    assert pool.start_time == start_time
    assert pool.stop_time == stop_time
    assert result == {
        "Dragon scimitar": {
            "completed_count": 3,
            "total_count": 4,
            "completion_rate": 0.75,
        },
        "Barrows gloves": {
            "completed_count": 1,
            "total_count": 4,
            "completion_rate": 0.25,
        },
    }


def test_milestone_completion_rates_returns_none_rate_without_snapshots(monkeypatch):
    pool = FakePool(
        [
            {
                "milestone_name": "Dragon scimitar",
                "total_count": 0,
                "completed_count": 0,
            },
        ]
    )

    async def fake_get_pool():
        return pool

    monkeypatch.setattr(db, "get_pool", fake_get_pool)

    result = asyncio.run(
        db.milestone_completion_rates(
            ["Dragon scimitar"],
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2026, 2, 1, tzinfo=UTC),
        )
    )

    assert result == {
        "Dragon scimitar": {
            "completed_count": 0,
            "total_count": 0,
            "completion_rate": None,
        },
    }


def test_milestone_completion_rates_rejects_future_stop_time():
    with pytest.raises(ValueError, match="stop_time cannot be in the future"):
        asyncio.run(
            db.milestone_completion_rates(
                ["Dragon scimitar"],
                datetime.now(UTC),
                datetime.now(UTC) + timedelta(seconds=1),
            )
        )


def test_milestone_completion_rates_rejects_naive_window():
    naive_start_time = datetime(2026, 1, 1, tzinfo=UTC).replace(tzinfo=None)

    with pytest.raises(ValueError, match="start_time must include timezone"):
        asyncio.run(
            db.milestone_completion_rates(
                ["Dragon scimitar"],
                naive_start_time,
                datetime(2026, 2, 1, tzinfo=UTC),
            )
        )


def test_milestone_completion_rates_rejects_empty_or_reversed_window():
    with pytest.raises(ValueError, match="start_time must be before stop_time"):
        asyncio.run(
            db.milestone_completion_rates(
                ["Dragon scimitar"],
                datetime(2026, 2, 1, tzinfo=UTC),
                datetime(2026, 1, 1, tzinfo=UTC),
            )
        )
