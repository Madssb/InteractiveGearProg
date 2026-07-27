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
from bot.metrics_commands import register_metrics_commands
from bot.milestone_commands import register_milestone_commands
from bot.moderation_commands import register_moderation_commands
from bot.report_logs import send_report_log
from db import user_report
from milestones import load_main_milestone_groups, load_milestone_names_by_id


ROOT_DIR = Path(__file__).resolve().parent.parent
MILESTONE_METADATA_PATH = ROOT_DIR / "data/generated/milestone-metadata.json"


# env variables

load_dotenv(ROOT_DIR / ".env")
BOTLOR_TOKEN = os.getenv("BOTLOR_TOKEN")
if not BOTLOR_TOKEN:
    raise SystemExit("BOTLOR_TOKEN is not set")

GUILD_ID_ = os.getenv("GUILD_ID")
if not GUILD_ID_:
    raise SystemExit("GUILD_ID is not set")
GUILD_ID = int(GUILD_ID_)

SUBMITTED_ANNOTATIONS_CHANNEL_ID_ = os.getenv("SUBMITTED_ANNOTATIONS_CHANNEL_ID")
if not SUBMITTED_ANNOTATIONS_CHANNEL_ID_:
    raise SystemExit("SUBMITTED_ANNOTATIONS_CHANNEL_ID is not set")
SUBMITTED_ANNOTATIONS_CHANNEL_ID = int(SUBMITTED_ANNOTATIONS_CHANNEL_ID_)

REPORT_LOGS_CHANNEL_ID_ = os.getenv("REPORT_LOGS_CHANNEL_ID")
if not REPORT_LOGS_CHANNEL_ID_:
    raise SystemExit("REPORT_LOGS_CHANNEL_ID is not set")
REPORT_LOGS_CHANNEL_ID = int(REPORT_LOGS_CHANNEL_ID_)

logger = logging.getLogger(__name__)


def load_milestone_metadata() -> dict[str, dict[str, Any]]:
    # used for milestone images
    with MILESTONE_METADATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


class BotClient(discord.Client):
    """Ladlorchart discord-bot client
    """
    def __init__(
        self,
        guild: discord.Object,
        submitted_annotations_channel_id: int,
        report_logs_channel_id: int,
    ) -> None:
        intents = discord.Intents.default()
        intents.reactions = True
        super().__init__(intents=intents)
        self.guild = guild
        self.submitted_annotations_channel_id = submitted_annotations_channel_id
        self.report_logs_channel_id = report_logs_channel_id
        self.tree = app_commands.CommandTree(self)
        self.milestone_metadata = load_milestone_metadata()
        self.milestone_ids = load_milestone_names_by_id()
        self.milestone_groups = load_main_milestone_groups()

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
            self.report_logs_channel_id,
        )
        register_moderation_commands(
            self.tree,
            self.guild,
            self.submitted_annotations_channel_id,
        )
        register_milestone_commands(
            self.tree,
            self.guild,
            self.milestone_ids,
            self.submitted_annotations_channel_id,
        )
        register_metrics_commands(
            self.tree,
            self.guild,
            self.milestone_ids,
            self.milestone_groups,
        )

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    guild = discord.Object(id=GUILD_ID)
    bot = BotClient(
        guild,
        SUBMITTED_ANNOTATIONS_CHANNEL_ID,
        REPORT_LOGS_CHANNEL_ID,
    )
    bot.run(BOTLOR_TOKEN)
