"""
Botlor discord bot source code
Currently supports making annotation submissions for the milestones.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any

import discord
from dotenv import load_dotenv
from discord import app_commands

from bot.annotation_commands import log_reaction_change, register_annotation_commands
from bot.milestone_commands import register_milestone_commands
from bot.moderation_commands import register_moderation_commands
from bot.report_logs import send_report_log
from db import user_report
from milestones import load_milestone_names_by_id


REPO_ROOT = Path(__file__).resolve().parents[1]
MILESTONE_METADATA_PATH = REPO_ROOT / "data/generated/milestone-metadata.json"
GUILD_ID_ENV = "GUILD_ID"
SUBMITTED_ANNOTATIONS_CHANNEL_ID_ENV = "SUBMITTED_ANNOTATIONS_CHANNEL_ID"
ANNOTARDATION_CHANNEL_ID_ENV = "ANNOTARDATION_CHANNEL_ID"
REPORT_LOGS_CHANNEL_ID_ENV = "REPORT_LOGS_CHANNEL_ID"
logger = logging.getLogger(__name__)


def load_milestone_metadata() -> dict[str, dict[str, Any]]:
    # used for milestone images
    with MILESTONE_METADATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


class BotClient(discord.Client):
    def __init__(
        self,
        guild: discord.Object,
        submitted_annotations_channel_id: int,
        annotardation_channel_id: int,
        report_logs_channel_id: int,
    ) -> None:
        intents = discord.Intents.default()
        intents.reactions = True
        super().__init__(intents=intents)
        self.guild = guild
        self.submitted_annotations_channel_id = submitted_annotations_channel_id
        self.annotardation_channel_id = annotardation_channel_id
        self.report_logs_channel_id = report_logs_channel_id
        self.tree = app_commands.CommandTree(self)
        self.milestone_metadata = load_milestone_metadata()
        self.milestone_ids = load_milestone_names_by_id()

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        await log_reaction_change(
            self,
            payload,
            self.submitted_annotations_channel_id,
        )

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        await log_reaction_change(
            self,
            payload,
            self.submitted_annotations_channel_id,
        )

    async def setup_hook(self) -> None:
        @self.tree.command(name="ping", description="Health check", guild=self.guild)
        async def ping(interaction: discord.Interaction) -> None:
            await interaction.response.send_message("im alive", ephemeral=True)

        register_annotation_commands(
            self.tree,
            self,
            self.guild,
            self.submitted_annotations_channel_id,
            self.annotardation_channel_id,
            self.report_logs_channel_id,
        )
        register_moderation_commands(self.tree, self.guild)
        register_milestone_commands(self.tree, self.guild, self.milestone_ids)

        @self.tree.command(name="report_user", description="Report a user", guild=self.guild)
        @app_commands.describe(
            username="The username or display name of the user being reported",
            reason="Why this user should be reviewed",
        )
        async def report_user_command(
            interaction: discord.Interaction,
            username: app_commands.Range[str, 1, 100],
            reason: app_commands.Range[str, 1, 1000],
        ) -> None:
            """Handle user reports."""
            reported_name = username.strip()
            if not reported_name:
                await interaction.response.send_message(
                    "Please include a username or display name.",
                    ephemeral=True,
                )
                return

            try:
                report_id = await user_report(
                    reported_name=reported_name,
                    reporter_user_id=interaction.user.id,
                    reason=reason,
                )
            except Exception:
                logger.exception(
                    "user report failed reported_name=%s reporter_user_id=%s",
                    reported_name,
                    interaction.user.id,
                )
                await interaction.response.send_message(
                    "Report failed. Contact Ladlor.",
                    ephemeral=True,
                )
                return

            embed = discord.Embed(
                title="User Report",
                description=reason,
            )
            embed.add_field(name="Report ID", value=str(report_id), inline=True)
            embed.add_field(name="Reported Name", value=reported_name, inline=False)
            embed.add_field(
                name="Reporter",
                value=f"{interaction.user.mention} (`{interaction.user.id}`)",
                inline=False,
            )
            log_sent = await send_report_log(
                self,
                self.report_logs_channel_id,
                embed,
            )
            if not log_sent:
                await interaction.response.send_message(
                    "Report saved, but I couldn't notify moderators. Contact Ladlor.",
                    ephemeral=True,
                )
                return

            await interaction.response.send_message(
                f"Report {report_id} submitted for {reported_name}.",
                ephemeral=True,
            )

        synced_commands = await self.tree.sync(guild=self.guild)
        logger.info(
            "synced discord commands guild_id=%s commands=%s",
            self.guild.id,
            ", ".join(command.name for command in synced_commands),
        )


def get_required_int_env(name: str) -> int:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is not set")

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv(REPO_ROOT / "backend/.env")
    load_dotenv(REPO_ROOT / "discord_bot/.env")
    token = os.getenv("BOTLOR_TOKEN")
    if not token:
        raise RuntimeError("BOTLOR_TOKEN environment variable is not set")
    guild = discord.Object(id=get_required_int_env(GUILD_ID_ENV))
    submitted_annotations_channel_id = get_required_int_env(
        SUBMITTED_ANNOTATIONS_CHANNEL_ID_ENV
    )
    annotardation_channel_id = get_required_int_env(ANNOTARDATION_CHANNEL_ID_ENV)
    report_logs_channel_id = get_required_int_env(REPORT_LOGS_CHANNEL_ID_ENV)

    bot = BotClient(
        guild,
        submitted_annotations_channel_id,
        annotardation_channel_id,
        report_logs_channel_id,
    )
    bot.run(token)
