"""Commands for browsing milestone IDs."""
import math

import discord
from discord import app_commands


MILESTONES_PER_PAGE = 20


class MilestoneListView(discord.ui.View):
    def __init__(
        self,
        milestones: list[tuple[int, str]],
        user_id: int,
        page: int = 0,
    ) -> None:
        super().__init__(timeout=300)
        self.milestones = milestones
        self.user_id = user_id
        self.page = page
        self.page_count = max(math.ceil(len(milestones) / MILESTONES_PER_PAGE), 1)
        self.update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True

        await interaction.response.send_message(
            "Run /milestones to browse your own list.",
            ephemeral=True,
        )
        return False

    def make_embed(self) -> discord.Embed:
        start = self.page * MILESTONES_PER_PAGE
        end = start + MILESTONES_PER_PAGE
        lines = [
            f"`{milestone_id}` {milestone_name}"
            for milestone_id, milestone_name in self.milestones[start:end]
        ]
        embed = discord.Embed(
            title="Milestone IDs",
            description="\n".join(lines) or "No milestones found.",
        )
        embed.set_footer(text=f"Page {self.page + 1}/{self.page_count}")
        return embed

    def update_buttons(self) -> None:
        self.previous_page.disabled = self.page <= 0
        self.next_page.disabled = self.page >= self.page_count - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.page = max(self.page - 1, 0)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.page = min(self.page + 1, self.page_count - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.make_embed(), view=self)


def register_milestone_commands(
    tree: app_commands.CommandTree,
    guild: discord.Object,
    milestones_by_id: dict[int, str],
) -> None:
    @tree.command(
        name="milestones",
        description="Browse milestone IDs",
        guild=guild,
    )
    async def milestones(interaction: discord.Interaction) -> None:
        """Show a paginated list of milestone IDs."""
        view = MilestoneListView(
            list(milestones_by_id.items()),
            interaction.user.id,
        )
        await interaction.response.send_message(
            embed=view.make_embed(),
            view=view,
            ephemeral=True,
        )
