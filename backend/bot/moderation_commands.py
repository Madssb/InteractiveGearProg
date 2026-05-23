"""Commands for moderation workflows."""
import logging

import discord
from discord import app_commands

from bot.report_logs import REPORT_PING_ROLE_ID
from db import resolve_report, unresolved_reports


logger = logging.getLogger(__name__)
MODERATOR_ROLE_ID = REPORT_PING_ROLE_ID


def register_moderation_commands(
    tree: app_commands.CommandTree,
    guild: discord.Object,
    submitted_annotations_channel_id: int,
) -> None:
    async def handle_moderation_command_error(
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(
            error,
            (app_commands.MissingPermissions, app_commands.MissingRole),
        ):
            await interaction.response.send_message(
                "You need the moderator role to use this command.",
                ephemeral=True,
            )
            return
        raise error

    @tree.command(
        name="resolve",
        description="Resolve a report",
        guild=guild,
    )
    @app_commands.describe(
        report_id="The report ID shown in the report log",
        verdict="The moderation verdict or resolution note",
    )
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_role(MODERATOR_ROLE_ID)
    async def resolve(
        interaction: discord.Interaction,
        report_id: int,
        verdict: app_commands.Range[str, 1, 1000],
    ) -> None:
        """Resolve a report."""
        try:
            result = await resolve_report(report_id, verdict)
        except Exception:
            logger.exception(
                "resolve report failed report_id=%s moderator_user_id=%s",
                report_id,
                interaction.user.id,
            )
            await interaction.response.send_message(
                "Failed to resolve report. Contact Ladlor.",
                ephemeral=True,
            )
            return

        status = result["status"]
        if status == "not_found":
            await interaction.response.send_message(
                f"I couldn't find an ongoing report with id {report_id}.",
                ephemeral=True,
            )
            return

        if status == "ambiguous":
            await interaction.response.send_message(
                f"Report id {report_id} matches more than one ongoing report. Contact Ladlor.",
                ephemeral=True,
            )
            return

        resolved_report = result["resolved_report"]
        if resolved_report is None:
            await interaction.response.send_message(
                "Report resolution ended in an unexpected state. Contact Ladlor.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Resolved {resolved_report['report_type']} report {report_id}.",
            ephemeral=True,
        )

    @resolve.error
    async def resolve_error(
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        await handle_moderation_command_error(interaction, error)

    @tree.command(
        name="view_unresolved",
        description="View unresolved report IDs",
        guild=guild,
    )
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_role(MODERATOR_ROLE_ID)
    async def view_unresolved(interaction: discord.Interaction) -> None:
        """List unresolved reports."""
        try:
            reports = await unresolved_reports()
        except Exception:
            logger.exception(
                "view unresolved reports failed moderator_user_id=%s",
                interaction.user.id,
            )
            await interaction.response.send_message(
                "Failed to fetch unresolved reports. Contact Ladlor.",
                ephemeral=True,
            )
            return

        if not reports:
            await interaction.response.send_message(
                "No unresolved reports.",
                ephemeral=True,
            )
            return

        annotation_ids = [
            str(report["report_id"])
            for report in reports
            if report["report_type"] == "annotation"
        ]
        user_ids = [
            str(report["report_id"])
            for report in reports
            if report["report_type"] == "user"
        ]
        lines = []
        if annotation_ids:
            lines.append(f"Annotation reports: {', '.join(annotation_ids)}")
        if user_ids:
            lines.append(f"User reports: {', '.join(user_ids)}")

        message = "\n".join(lines)
        if len(message) > 1900:
            message = message[:1900].rsplit(",", 1)[0] + "\nList truncated."

        await interaction.response.send_message(message, ephemeral=True)

    @view_unresolved.error
    async def view_unresolved_error(
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        await handle_moderation_command_error(interaction, error)
