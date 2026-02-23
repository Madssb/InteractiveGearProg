import os

import discord
from discord import app_commands


class BotClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        @self.tree.command(name="ping", description="Health check")
        async def ping(interaction: discord.Interaction) -> None:
            await interaction.response.send_message("im alive", ephemeral=True)

        await self.tree.sync()


if __name__ == "__main__":
    token = os.getenv("BOTLOR_TOKEN")
    if not token:
        raise RuntimeError("BOTLOR_TOKEN environment variable is not set")

    bot = BotClient()
    bot.run(token)
