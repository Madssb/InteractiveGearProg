"""SQL statements for report management"""

from typing import Literal, TypedDict

import asyncpg

from backend.database.shared import get_pool


class Report(TypedDict):
    report_type: Literal["annotation", "user"]
    report_id: int


class ResolveReportResult(TypedDict):
    status: Literal["resolved", "not_found", "ambiguous"]
    resolved_report: Report | None


async def next_report_id(connection: asyncpg.Connection) -> int:
    """Report ID generator.

    Args:
        connection: connection to lock.

    Returns:
        Generated report ID.

    Raises:
        ValueError: Failed to generate report ID.
    """
    await connection.execute("SELECT pg_advisory_xact_lock(1506719382213099610)")
    report_id = await connection.fetchval(
        """
        SELECT COALESCE(MAX(report_id), 0) + 1
        FROM (
            SELECT report_id FROM annotation_reports
            UNION ALL
            SELECT report_id FROM user_reports
        ) AS report_ids
        """
    )
    if report_id is None:
        raise ValueError("Failed to generate report ID.")
    return report_id


async def annotation_report(
    annotation_id: int,
    reporter_user_id: int,
    reason: str,
) -> int:
    """Add annotation report record.

    Args:
        annotation_id: ID of reported annotation.
        reported_user_id: Discord user ID of annotation author.
        reason: report text content.

    Returns:
        Report ID.
    """
    pool = await get_pool()
    async with pool.acquire() as connection, connection.transaction():
        report_id = await next_report_id(connection)  # type: ignore
        await connection.execute(
            """
                INSERT INTO annotation_reports (
                    report_id,
                    annotation_id,
                    reporter_user_id,
                    reason
                )
                OVERRIDING SYSTEM VALUE
                VALUES ($1, $2, $3, $4)
                """,
            report_id,
            annotation_id,
            reporter_user_id,
            reason,
        )
        return report_id


async def user_report(
    reported_name: str,
    reporter_user_id: int,
    reason: str,
) -> int:
    """Add user report record.

    Args:
        reported_name: discord display name of reported user at the time of report.
        reporter_user_id: Discord user ID of report submitter.
        reason: report text content.

    Returns:
        Report ID.
    """
    pool = await get_pool()
    async with pool.acquire() as connection, connection.transaction():
        report_id = await next_report_id(connection)  # type: ignore
        await connection.execute(
            """
                INSERT INTO user_reports (
                    report_id,
                    reported_name,
                    reporter_user_id,
                    reason
                )
                OVERRIDING SYSTEM VALUE
                VALUES ($1, $2, $3, $4)
                """,
            report_id,
            reported_name,
            reporter_user_id,
            reason,
        )
        return report_id


async def resolve_report(report_id: int, verdict: str) -> ResolveReportResult:
    """Resolve any report if id exists and not already resolved.

    Looks for report id in annotation_reports or user_reports where unresolved is true.
    Sets corresponding record to resolved with updating rows accordingly.

    Args:
        report_id: ID of report to resolve.
        verdict: Report decision.

    Returns:
        Resolved report record.
    """
    pool = await get_pool()
    async with pool.acquire() as connection, connection.transaction():
        annotation_report_id = await connection.fetchval(
            """
                SELECT report_id
                FROM annotation_reports
                WHERE report_id = $1
                    AND ongoing = true
                FOR UPDATE
                """,
            report_id,
        )
        if annotation_report_id is not None:
            table_name = "annotation_report"
            report_type = "annotation"

        else:
            user_report_id = await connection.fetchval(
                """
                    SELECT report_id
                    FROM user_reports
                    WHERE report_id = $1
                        AND ongoing = true
                    FOR UPDATE
                    """,
                report_id,
            )
            if user_report_id is None:
                return {"status": "not_found", "resolved_report": None}
            table_name = "user_reports"
            report_type = "user"

        await connection.execute(
            f"""
                UPDATE {table_name}
                SET ongoing = false,
                    verdict = $1,
                    resolved_at = now()
                WHERE report_id = $2
                """,
            verdict,
            report_id,
        )
        return {
            "status": "resolved",
            "resolved_report": {
                "report_type": report_type,
                "report_id": report_id,
            },
        }


async def unresolved_reports() -> list[Report] | None:
    """Get unresolved reports.

    Returns:
        Report records for unresolved if exists.
    """
    pool = await get_pool()
    records = await pool.fetch(
        """
        SELECT 'annotation' AS report_type, report_id
        FROM annotation_reports
        WHERE ongoing = true

        UNION ALL

        SELECT 'user' AS report_type, report_id
        FROM user_reports
        WHERE ongoing = true

        ORDER BY report_id
        """
    )
    if not records:
        return None
    return [
        {"report_type": record["report_type"], "report_id": record["report_id"]}
        for record in records
    ]
