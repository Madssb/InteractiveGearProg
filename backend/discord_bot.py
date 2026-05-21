"""
Botlor discord bot source code
Currently support making annotation submissions for the milestones.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any

import discord
from dotenv import load_dotenv
from discord import app_commands

from db import annotation_report, annotation_submission, annotation_vote
from milestones import load_milestone_names_by_id


REPO_ROOT = Path(__file__).resolve().parents[1]
MILESTONE_METADATA_PATH = REPO_ROOT / "data/generated/milestone-metadata.json"
GUILD_ID = discord.Object(id=1460320916637749321)
SUBMITTED_ANNOTATIONS_CHANNEL_ID = 1506720845450576083  # testing
VOTE_EMOJIS = {"👍", "👎"}
logger = logging.getLogger(__name__)


def load_milestone_metadata() -> dict[str, dict[str, Any]]:
    # used for milestone images
    with MILESTONE_METADATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


class BotClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.reactions = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.milestone_metadata = load_milestone_metadata()
        self.milestone_ids = load_milestone_names_by_id()

    async def fetch_or_get_channel(self, channel_id: int) -> discord.abc.GuildChannel | None:
        channel = self.get_channel(channel_id)
        if channel is not None:
            return channel

        logger.warning("channel not cached; fetching channel_id=%s", channel_id)
        try:  # fallback if channel is not cached
            fetched_channel = await self.fetch_channel(channel_id)
        except discord.DiscordException:
            logger.exception("failed to fetch channel_id=%s", channel_id)
            return None

        if isinstance(fetched_channel, discord.abc.GuildChannel):
            return fetched_channel
        return None

    async def log_reaction_change(
        self,
        payload: discord.RawReactionActionEvent,
    ) -> None:
        """Catch upvotes and downvotes for submissions
        """
        if payload.channel_id != SUBMITTED_ANNOTATIONS_CHANNEL_ID:
            return
        if self.user is not None and payload.user_id == self.user.id: # ignore bot self-reacts
            return

        emoji = str(payload.emoji)
        if emoji not in VOTE_EMOJIS:
            return

        channel = await self.fetch_or_get_channel(payload.channel_id)
        if channel is None:
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.DiscordException:
            logger.exception(
                "failed to fetch reacted message channel_id=%s message_id=%s",
                payload.channel_id,
                payload.message_id,
            )
            return

        vote_counts = {emoji: 0 for emoji in VOTE_EMOJIS}
        for reaction in message.reactions:
            reaction_emoji = str(reaction.emoji)
            if reaction_emoji in vote_counts:
                vote_counts[reaction_emoji] = max(reaction.count - 1, 0)

        await annotation_vote(
            message_id=payload.message_id,
            up_count=vote_counts["👍"],
            down_count=vote_counts["👎"],
        )

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        await self.log_reaction_change(payload)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        await self.log_reaction_change(payload)

    async def setup_hook(self) -> None:
        @self.tree.command(name="ping", description="Health check", guild=GUILD_ID)
        async def ping(interaction: discord.Interaction) -> None:
            await interaction.response.send_message("im alive", ephemeral=True)

        @self.tree.command(name="annotate", description="Make an annotation for a milestone step", guild=GUILD_ID)
        @app_commands.describe(
            milestone_id="The milestone step this annotation is for",
            contents="The annotation contents to submit",
        )
        async def annotate(
            interaction: discord.Interaction,
            milestone_id: int,
            contents: app_commands.Range[str, 1, 1800],
        ) -> None:
            """Handle annotation submissions
            """
            # valid milestone required
            milestone_name = self.milestone_ids.get(milestone_id)
            if milestone_name is None:
                await interaction.response.send_message(
                    f"I don't recognize milestone id {milestone_id}.",
                    ephemeral=True,
                )
                return

            # img required
            metadata = self.milestone_metadata.get(milestone_name)
            if metadata is None:
                await interaction.response.send_message(
                    f"Milestone id {milestone_id} exists, but I couldn't find its metadata.",
                    ephemeral=True,
                )
                return
            img = metadata["imgUrl"]

            # channel access required
            channel = interaction.client.get_channel(SUBMITTED_ANNOTATIONS_CHANNEL_ID)
            if not isinstance(channel, discord.abc.Messageable):
                await interaction.response.send_message(
                    "I couldn't find the annotation submission channel.",
                    ephemeral=True,
                )
                return

            # formatting
            display_name = interaction.user.display_name
            header = f"**Milestone annotation submission for** __**{milestone_name}**__\n"
            submitted_by = f"*submitted by* __*{display_name}*__\n"
            spacing = "\n"
            submission = f"> {contents}\n"
            footer = "*score this submission with a thumbs up or thumbs down*"
            embed = discord.Embed(
                description=header + submitted_by + spacing + submission + footer
            )
            embed.set_thumbnail(url=img)
            message = await channel.send(embed=embed)
            try:
                await message.add_reaction("👍")
                await message.add_reaction("👎")
                annotation_id = await annotation_submission(
                    message_id=message.id,
                    milestone_id=milestone_id,
                    user_id=interaction.user.id,
                    annotation_text=contents
                )
                embed.set_footer(text=f"Annotation ID: {annotation_id}")
                await message.edit(embed=embed)
            except Exception:
                logger.exception(
                    "annotation submission failed message_id=%s milestone_id=%s user_id=%s",
                    message.id,
                    milestone_id,
                    interaction.user.id,
                )
                try:
                    await message.delete()
                except discord.DiscordException:
                    logger.exception(
                        "failed to delete failed annotation message_id=%s",
                        message.id,
                    )
                await interaction.response.send_message(
                    "Submission failed, contact Ladlor.",
                    ephemeral=True,
                )
                return

            await interaction.response.send_message("Annotation submitted.", ephemeral=True)

        @self.tree.command(name="report", description="Report an annotation", guild=GUILD_ID)
        @app_commands.describe(
            annotation_id="The annotation ID shown on the annotation",
            reason="Why this annotation should be reviewed",
        )
        async def report(
            interaction: discord.Interaction,
            annotation_id: int,
            reason: app_commands.Range[str, 1, 1000],
        ) -> None:
            """Handle annotation reports."""
            try:
                await annotation_report(
                    annotation_id=annotation_id,
                    reporter_user_id=interaction.user.id,
                    reason=reason,
                )
            except Exception:
                logger.exception(
                    "annotation report failed annotation_id=%s reporter_user_id=%s",
                    annotation_id,
                    interaction.user.id,
                )
                await interaction.response.send_message(
                    "Report failed. Check the annotation ID or contact Ladlor.",
                    ephemeral=True,
                )
                return

            await interaction.response.send_message("Report submitted.", ephemeral=True)

        await self.tree.sync(guild=GUILD_ID)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv(REPO_ROOT / "backend/.env")
    load_dotenv(REPO_ROOT / "discord_bot/.env")
    token = os.getenv("BOTLOR_TOKEN")
    if not token:
        raise RuntimeError("BOTLOR_TOKEN environment variable is not set")

    bot = BotClient()
    bot.run(token)
