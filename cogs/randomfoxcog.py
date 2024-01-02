import discord
from discord import app_commands
from discord.ext import commands

import requests
import io

from util.const import labowor
from util.msgutil import devcheck


class RandomFoxCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)
        

    # send a random fox
    @app_commands.command(name="fox", description="Image of a random fox")
    async def random_fox(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            img = requests.get("https://api.tinyfox.dev/img?animal=fox").content
            await interaction.followup.send(file=discord.File(io.BytesIO(img), "fox.png"))
        except Exception as e:
            await interaction.followup.send(str(e))




async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RandomFoxCog(bot), guild=labowor)
