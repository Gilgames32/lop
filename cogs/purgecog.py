import discord
from discord import app_commands
from discord.ext import commands

from util.const import labowor
from util.msgutil import devcheck


class PurgeCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    # purge her own messages
    @app_commands.command(name="purr", description="Purge her own messages")
    @app_commands.describe(limit="number of messages to fetch")
    async def purge_self(self, interaction: discord.Interaction, limit: int):
        if not await devcheck(interaction):
            return
        deleted = await interaction.channel.purge(
            limit=limit, check=lambda message: message.author.id == self.bot.user.id
        )
        await interaction.response.send_message(
            f"Purrged {len(deleted)} messages", ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PurgeCog(bot), guild=labowor)
