"""Commands for annotation submissions."""
import logging

import discord
from discord import app_commands

from bot.report_logs import send_report_log
from db import (
    annotation_report,
    annotation_submission,
    annotation_vote,
    get_annotation_owner_and_message_ids,
    remove_annotation_record,
)


logger = logging.getLogger(__name__)
ANNOTATE_REQUIRED_ROLE_ID = 1507645289509552250
VOTE_EMOJIS = {"👍", "👎"}


async def fetch_or_get_channel(
    client: discord.Client,
    channel_id: int,
) -> discord.abc.GuildChannel | None:
    channel = client.get_channel(channel_id)
    if channel is not None:
        return channel

    logger.warning("channel not cached; fetching channel_id=%s", channel_id)
    try:
        fetched_channel = await client.fetch_channel(channel_id)
    except discord.DiscordException:
        logger.exception("failed to fetch channel_id=%s", channel_id)
        return None

    if isinstance(fetched_channel, discord.abc.GuildChannel):
        return fetched_channel
    return None


async def log_reaction_change(
    client: discord.Client,
    payload: discord.RawReactionActionEvent,
    submitted_annotations_channel_id: int,
) -> None:
    """Catch upvotes and downvotes for annotation submissions."""
    if payload.channel_id != submitted_annotations_channel_id:
        return
    if client.user is not None and payload.user_id == client.user.id:
        return

    emoji = str(payload.emoji)
    if emoji not in VOTE_EMOJIS:
        return

    channel = await fetch_or_get_channel(client, payload.channel_id)
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


def register_annotation_commands(
    tree: app_commands.CommandTree,
    client: discord.Client,
    guild: discord.Object,
    submitted_annotations_channel_id: int,
    report_logs_channel_id: int,
) -> None:
    async def handle_annotation_report(
        interaction: discord.Interaction,
        annotation_id: int,
        reason: str,
    ) -> None:
        annotation_ids = await get_annotation_owner_and_message_ids(annotation_id)
        if annotation_ids is None:
            await interaction.response.send_message(
                f"I don't recognize annotation id {annotation_id}.",
                ephemeral=True,
            )
            return

        try:
            report_id = await annotation_report(
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

        embed = discord.Embed(
            title="Annotation Report",
            description=reason,
        )
        embed.add_field(name="Report ID", value=str(report_id), inline=True)
        embed.add_field(name="Annotation ID", value=str(annotation_id), inline=True)
        embed.add_field(
            name="Reporter",
            value=f"{interaction.user.mention} (`{interaction.user.id}`)",
            inline=False,
        )
        embed.add_field(
            name="Annotation Author ID",
            value=str(annotation_ids["user_id"]),
            inline=True,
        )
        embed.add_field(
            name="Message ID",
            value=str(annotation_ids["message_id"]),
            inline=True,
        )
        log_sent = await send_report_log(client, report_logs_channel_id, embed)
        if not log_sent:
            await interaction.response.send_message(
                "Report saved, but I couldn't notify moderators. Contact Ladlor.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Report {report_id} submitted for annotation {annotation_id}.",
            ephemeral=True,
        )

    @tree.command(
        name="annotate",
        description="Make an annotation for a milestone step",
        guild=guild,
    )
    @app_commands.describe(
        milestone_id="ID for the milestone this annotation is for. You can copy this by right clicking the milestone on the chart.",
        contents="The annotation contents to submit",
    )
    @app_commands.checks.has_role(ANNOTATE_REQUIRED_ROLE_ID)
    async def submit_annotation(
        interaction: discord.Interaction,
        milestone_id: int,
        contents: app_commands.Range[str, 1, 1800],
    ) -> None:
        """Handle annotation submissions."""
        milestone_name = client.milestone_ids.get(milestone_id)
        if milestone_name is None:
            await interaction.response.send_message(
                f"I don't recognize milestone id {milestone_id}.",
                ephemeral=True,
            )
            return

        metadata = client.milestone_metadata.get(milestone_name)
        if metadata is None:
            await interaction.response.send_message(
                f"Milestone id {milestone_id} exists, but I couldn't find its metadata.",
                ephemeral=True,
            )
            return
        img = metadata["imgUrl"]

        channel = interaction.client.get_channel(submitted_annotations_channel_id)
        if not isinstance(channel, discord.abc.Messageable):
            await interaction.response.send_message(
                "I couldn't find the annotation submission channel.",
                ephemeral=True,
            )
            return

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
                user_display_name=display_name,
                annotation_text=contents,
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

    @submit_annotation.error
    async def submit_annotation_error(
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(
                "You need the Annotations role to use this command. Contact Ladlor if interested",
                ephemeral=True,
            )
            return
        raise error

    @tree.command(
        name="remove_annotation",
        description="Remove the specified annotation if you're the author or hold sufficient privilidges.",
        guild=guild
    )
    @app_commands.describe(
        annotation_id="ID for annotation to remove."
    )
    async def remove_annotation(
        interaction: discord.Interaction,
        annotation_id: int
    ) -> None:
        """Handle annotation remove requests"""
        
        admin_user_ids = [
            163892364681674753 # madlor
        ]
        user_id = interaction.user.id
        annotation_ids = await get_annotation_owner_and_message_ids(annotation_id)
        if annotation_ids is None:
            await interaction.response.send_message(
                f"I don't recognize annotation id {annotation_id}.",
                ephemeral=True,
            )
            return
        annotation_author_user_id = annotation_ids["user_id"]
        message_id = annotation_ids["message_id"]
        
        if user_id not in admin_user_ids and user_id != annotation_author_user_id:
            await interaction.response.send_message(
                f"Insufficient privileges for deleting {annotation_id}. Must be moderator or author.",
                ephemeral=True,
            )
            return

        try:
            successful_remove = await remove_annotation_record(annotation_id)
        except Exception:
            logger.exception(
                "failed to remove annotation record annotation_id=%s user_id=%s",
                annotation_id,
                user_id,
            )
            await interaction.response.send_message(
                f"Failed to remove annotation with id {annotation_id}.",
                ephemeral=True,
            )
            return

        if not successful_remove:
            await interaction.response.send_message(
                f"I couldn't find annotation id {annotation_id} to remove.",
                ephemeral=True,
            )
            return

        try:
            channel = interaction.client.get_channel(submitted_annotations_channel_id)
            if channel is None:
                channel = await interaction.client.fetch_channel(
                    submitted_annotations_channel_id
                )
            message = await channel.fetch_message(message_id)
            await message.delete()
        except (AttributeError, discord.DiscordException):
            logger.exception(
                "annotation record removed but discord message deletion failed "
                "annotation_id=%s message_id=%s",
                annotation_id,
                message_id,
            )
            await interaction.response.send_message(
                f"Removed annotation {annotation_id}, but failed to delete its Discord message.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully removed annotation with id {annotation_id}.",
            ephemeral=True,
        )

    @tree.command(
        name="report_annotation",
        description="Report an annotation",
        guild=guild,
    )
    @app_commands.describe(
        annotation_id="The annotation ID shown on the annotation",
        reason="Why this annotation should be reviewed",
    )
    async def report_annotation(
        interaction: discord.Interaction,
        annotation_id: int,
        reason: app_commands.Range[str, 1, 1000],
    ) -> None:
        """Handle annotation reports."""
        await handle_annotation_report(interaction, annotation_id, reason)

    @tree.command(
        name="report",
        description="Report an annotation",
        guild=guild,
    )
    @app_commands.describe(
        annotation_id="The annotation ID shown on the annotation",
        reason="Why this annotation should be reviewed",
    )
    async def report_annotation_alias(
        interaction: discord.Interaction,
        annotation_id: int,
        reason: app_commands.Range[str, 1, 1000],
    ) -> None:
        """Handle annotation reports through the legacy report command."""
        await handle_annotation_report(interaction, annotation_id, reason)
