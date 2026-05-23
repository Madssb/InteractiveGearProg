"""Commands for public chart metrics."""
import math

import discord
from discord import app_commands

from db import milestone_completion_rate, milestone_skip_rate


def skip_threshold(remaining_milestone_count: int) -> int:
    return math.floor(min(5, max(remaining_milestone_count / 10, 1)))


def metric_name(milestone_name: str) -> str:
    parts = milestone_name.split(maxsplit=1)
    if len(parts) == 2 and parts[0].isdigit():
        return parts[1]
    return milestone_name


def milestone_context_from_groups(
    milestone_name: str,
    milestone_groups: list[list[str]],
) -> tuple[str, list[str]] | None:
    for group_index, group in enumerate(milestone_groups):
        for candidate_name in group:
            if milestone_name not in {candidate_name, metric_name(candidate_name)}:
                continue
            later_milestone_names = [
                later_milestone_name
                for later_group in milestone_groups[group_index + 1:]
                for later_milestone_name in later_group
            ]
            return candidate_name, later_milestone_names
    return None


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

        milestone_context = milestone_context_from_groups(
            milestone_name,
            milestone_groups,
        )
        snapshot_milestone_name = (
            milestone_context[0]
            if milestone_context is not None
            else milestone_name
        )

        await interaction.response.defer(thinking=True)
        metric = await milestone_completion_rate(snapshot_milestone_name)
        total_count = metric["total_count"]
        completed_count = metric["completed_count"]
        completion_rate_value = metric["completion_rate"]

        embed = discord.Embed(title="Milestone Completion Rate")
        embed.add_field(
            name="Milestone",
            value=f"`{milestone_id}` {milestone_name}",
            inline=False,
        )
        if completion_rate_value is None:
            embed.description = "No player milestone snapshots have been recorded yet."
        else:
            percentage = completion_rate_value * 100
            embed.add_field(
                name="Completion Rate",
                value=f"{percentage:.2f}% (`{completed_count}/{total_count}` snapshots)",
                inline=False,
            )
            embed.add_field(
                name="Definition",
                value="`P_j = (1 / N) sum_i x_ij`",
                inline=False,
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

        milestone_context = milestone_context_from_groups(
            milestone_name,
            milestone_groups,
        )
        if milestone_context is None:
            await interaction.response.send_message(
                f"I couldn't find milestone id {milestone_id} in the main chart sequence.",
                ephemeral=True,
            )
            return

        snapshot_milestone_name, subsequent_milestone_names = milestone_context
        threshold = skip_threshold(len(subsequent_milestone_names))

        await interaction.response.defer(thinking=True)
        metric = await milestone_skip_rate(
            snapshot_milestone_name,
            subsequent_milestone_names,
            threshold,
        )
        eligible_count = metric["eligible_count"]
        skipped_count = metric["skipped_count"]
        skip_rate_value = metric["skip_rate"]

        embed = discord.Embed(title="Milestone Skip Rate")
        embed.add_field(
            name="Milestone",
            value=f"`{milestone_id}` {milestone_name}",
            inline=False,
        )
        embed.add_field(
            name="Eligibility",
            value=(
                f"At least `{threshold}` later milestone"
                f"{'' if threshold == 1 else 's'} completed."
            ),
            inline=False,
        )
        if skip_rate_value is None:
            embed.description = "No skip-eligible snapshots have been recorded for this milestone."
        else:
            percentage = skip_rate_value * 100
            embed.add_field(
                name="Skip Rate",
                value=f"{percentage:.2f}% (`{skipped_count}/{eligible_count}` eligible snapshots)",
                inline=False,
            )
            embed.add_field(
                name="Definition",
                value="`S_j = sum_i y_ij / sum_i f_ij`",
                inline=False,
            )

        await interaction.followup.send(embed=embed)
