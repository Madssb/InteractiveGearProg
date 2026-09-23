"""Commands for public chart metrics."""

import discord
from discord import app_commands

from backend.database.chart_analytics import (
    milestone_completion_rate,
    milestone_skip_rate,
)
from backend.milestones import get_skip_threshold, get_subsequent_milestones


def register_metrics_commands(
    tree: app_commands.CommandTree,
    guild: discord.Object,
    milestones_by_id: dict[int, str],
    milestone_groups: list[list[str]],
) -> None:
    @tree.command(
        name="completion_rate",
        description="Show the completion rate for a milestone",
        guild=guild,
    )
    @app_commands.describe(
        milestone_id="ID for the milestone to inspect.",
    )
    async def completion_rate(
        interaction: discord.Interaction,
        milestone_id: int,
    ) -> None:
        """Show public completion rate for a milestone."""
        milestone_name = milestones_by_id.get(milestone_id)
        if milestone_name is None:
            await interaction.response.send_message(
                f"I don't recognize milestone id {milestone_id}.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)
        metric = await milestone_completion_rate(milestone_name)
        total_count = metric["total_count"]
        completed_count = metric["completed_count"]
        completion_rate_value = metric["completion_rate"]

        embed = discord.Embed(title=f"Completion rate: {milestone_name}")
        if completion_rate_value is None:
            embed.description = "No player milestone snapshots have been recorded yet."
        else:
            percentage = completion_rate_value * 100
            embed.description = (
                f"{percentage:.2f}% ({completed_count}/{total_count} snapshots)"
            )

        await interaction.followup.send(embed=embed)

    @tree.command(
        name="skip_rate",
        description="Show the skip rate for a milestone",
        guild=guild,
    )
    @app_commands.describe(
        milestone_id="ID for the milestone to inspect.",
    )
    async def skip_rate(
        interaction: discord.Interaction,
        milestone_id: int,
    ) -> None:
        """Show public skip rate for a milestone."""
        milestone_name = milestones_by_id.get(milestone_id)
        if milestone_name is None:
            await interaction.response.send_message(
                f"I don't recognize milestone id {milestone_id}.",
                ephemeral=True,
            )
            return
        subsequent_milestones = get_subsequent_milestones(milestone_name)
        if subsequent_milestones is None:
            await interaction.response.send_message(
                f"Subsequent milestones couldn't be found for milestone {milestone_name}.",
                ephemeral=True,
            )
            return
        skip_threshold = get_skip_threshold(len(subsequent_milestones))
        await interaction.response.defer(thinking=True)
        metric = await milestone_skip_rate(
            milestone_name,
            subsequent_milestones,
            skip_threshold,
        )
        eligible_count = metric["eligible_count"]
        skipped_count = metric["skipped_count"]
        skip_rate_value = metric["skip_rate"]

        embed = discord.Embed(title=f"Skip rate: {milestone_name}")
        if skip_rate_value is None:
            embed.description = (
                "No skip-eligible snapshots have been recorded for this milestone."
            )
        else:
            percentage = skip_rate_value * 100
            embed.description = (
                f"{percentage:.2f}% ({skipped_count}/{eligible_count} snapshots)"
            )

        await interaction.followup.send(embed=embed)
