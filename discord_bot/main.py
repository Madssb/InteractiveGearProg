import json
import os
from pathlib import Path
from typing import Any

import discord
from dotenv import load_dotenv
from discord import app_commands


REPO_ROOT = Path(__file__).resolve().parents[1]
MILESTONE_METADATA_PATH = REPO_ROOT / "data/generated/milestone-metadata.json"
MILESTONE_IDS_PATH = REPO_ROOT / "data/logic/milestone-ids.json"
GUILD_ID = discord.Object(id=1460320916637749321)
SUBMITTED_ANNOTATIONS_CHANNEL_ID = 1506720845450576083  # testing


def load_milestone_metadata() -> dict[str, dict[str, Any]]:
    with MILESTONE_METADATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_milestone_ids() -> dict[int, str]:
    with MILESTONE_IDS_PATH.open("r", encoding="utf-8") as f:
        raw_milestone_ids = json.load(f)
    return {
        int(milestone_id): milestone
        for milestone_id, milestone in raw_milestone_ids.items()
    }


class BotClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.milestone_metadata = load_milestone_metadata()
        self.milestone_ids = load_milestone_ids()

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
            milestone = self.milestone_ids.get(milestone_id)
            if milestone is None:
                await interaction.response.send_message(
                    f"I don't recognize milestone id {milestone_id}.",
                    ephemeral=True,
                )
                return

            metadata = self.milestone_metadata.get(milestone)
            if metadata is None:
                await interaction.response.send_message(
                    f"Milestone id {milestone_id} exists, but I couldn't find its metadata.",
                    ephemeral=True,
                )
                return
            img = metadata["imgUrl"]

            channel = interaction.client.get_channel(SUBMITTED_ANNOTATIONS_CHANNEL_ID)
            if not isinstance(channel, discord.abc.Messageable):
                await interaction.response.send_message(
                    "I couldn't find the annotation submission channel.",
                    ephemeral=True,
                )
                return

            display_name = interaction.user.display_name

            header = f"**Milestone annotation submission** from ***{display_name}***\n"
            spacing = "\n"
            submission = f"> {contents}\n"
            footer = "*score this submission with a thumbs up or thumbs down reaction*"
            embed = discord.Embed(description=header + spacing + submission + footer)
            embed.set_thumbnail(url=img)

            await channel.send(embed=embed)

            await interaction.response.send_message("Annotation submitted.", ephemeral=True)

        await self.tree.sync(guild=GUILD_ID)


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("BOTLOR_TOKEN")
    if not token:
        raise RuntimeError("BOTLOR_TOKEN environment variable is not set")

    bot = BotClient()
    bot.run(token)
