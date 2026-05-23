"""Commands for browsing milestone IDs."""
import math

import discord
from discord import app_commands

from db import annotated_milestone_ids, milestone_annotation_message_lookup


MILESTONES_PER_PAGE = 20
ANNOTATION_LINKS_PER_PAGE = 10


class MilestoneListView(discord.ui.View):
    def __init__(
        self,
        milestones: list[tuple[int, str]],
        user_id: int,
        title: str,
        empty_text: str,
        page: int = 0,
    ) -> None:
        super().__init__(timeout=300)
        self.milestones = milestones
        self.user_id = user_id
        self.title = title
        self.empty_text = empty_text
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
            title=self.title,
            description="\n".join(lines) or self.empty_text,
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


class AnnotationLinkView(discord.ui.View):
    def __init__(
        self,
        links: list[tuple[int, str]],
        user_id: int,
        milestone_name: str,
        page: int = 0,
    ) -> None:
        super().__init__(timeout=300)
        self.links = links
        self.user_id = user_id
        self.milestone_name = milestone_name
        self.page = page
        self.page_count = max(
            math.ceil(len(links) / ANNOTATION_LINKS_PER_PAGE),
            1,
        )
        self.update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True

        await interaction.response.send_message(
            "Run /milestone_annotations_lookup to browse your own links.",
            ephemeral=True,
        )
        return False

    def make_embed(self) -> discord.Embed:
        start = self.page * ANNOTATION_LINKS_PER_PAGE
        end = start + ANNOTATION_LINKS_PER_PAGE
        lines = [
            f"Annotation `{annotation_id}`: {message_url}"
            for annotation_id, message_url in self.links[start:end]
        ]
        embed = discord.Embed(
            title=f"Annotation Links: {self.milestone_name}",
            description="\n".join(lines) or "No annotations found.",
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
    submitted_annotations_channel_id: int,
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
            "Milestone IDs",
            "No milestones found.",
        )
        await interaction.response.send_message(
            embed=view.make_embed(),
            view=view,
            ephemeral=True,
        )

    @tree.command(
        name="non_annotated_milestones",
        description="Browse milestone IDs with no annotations yet",
        guild=guild,
    )
    async def non_annotated_milestones(interaction: discord.Interaction) -> None:
        """Show a paginated list of milestone IDs without annotations."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        annotated_ids = await annotated_milestone_ids()
        milestones_without_annotations = [
            (milestone_id, milestone_name)
            for milestone_id, milestone_name in milestones_by_id.items()
            if milestone_id not in annotated_ids
        ]
        view = MilestoneListView(
            milestones_without_annotations,
            interaction.user.id,
            "Milestones Without Annotations",
            "Every milestone has at least one annotation.",
        )
        await interaction.followup.send(
            embed=view.make_embed(),
            view=view,
            ephemeral=True,
        )

    @tree.command(
        name="milestone_annotations_lookup",
        description="Get Discord message links for a milestone's annotations",
        guild=guild,
    )
    @app_commands.describe(
        milestone_id="ID for the milestone to look up.",
    )
    async def milestone_annotations_lookup_command(
        interaction: discord.Interaction,
        milestone_id: int,
    ) -> None:
        """Show links to Discord annotation messages for a milestone."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        milestone_name = milestones_by_id.get(milestone_id)
        if milestone_name is None:
            await interaction.followup.send(
                f"I don't recognize milestone id {milestone_id}.",
                ephemeral=True,
            )
            return

        annotation_messages = await milestone_annotation_message_lookup(milestone_id)
        links = [
            (
                row["annotation_id"],
                "https://discord.com/channels/"
                f"{guild.id}/{submitted_annotations_channel_id}/{row['message_id']}",
            )
            for row in annotation_messages
        ]
        view = AnnotationLinkView(
            links,
            interaction.user.id,
            milestone_name,
        )
        await interaction.followup.send(
            embed=view.make_embed(),
            view=view,
            ephemeral=True,
        )
