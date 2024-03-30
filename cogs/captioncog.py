import discord
from discord import app_commands
from discord.ext import commands

from util.const import labowor


class CaptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    # rss feedparse for twokinds
    @app_commands.command(name="caption", description="caption media")
    async def twokinds(self, interaction: discord.Interaction, link: str, caption: str):
        await interaction.response.defer()
        # TODO: make async

        await interaction.followup.send("", file=discord.File())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CaptionCog(bot), guild=labowor)
