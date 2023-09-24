import discord
from discord import app_commands
from discord.ext import commands

from const import labowor, LOPDEBUG

class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)
        
    # debug ping, also sets the status, snowflake
    @app_commands.command(name="debug", description="Debug ping", guild=labowor)
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message(":3")
        if LOPDEBUG:
            return
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="Gil's nightmares"
            )
        )

    # todo: proper status setter (not like im gonna use it)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatusCog(bot), guild=labowor)