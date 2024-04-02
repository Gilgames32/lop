import discord
from discord import app_commands
from discord.ext import commands

from util.const import labowor
from util.msgutil import devcheck, errorembed, errorrespond

from caption.src.pipeline import caption

class CaptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    # caption gifs and stuff
    @app_commands.command(name="caption", description="caption media")
    async def twokinds(self, interaction: discord.Interaction, text: str, link: str = None, image: discord.Attachment = None):
        if not await devcheck(interaction):
            return
        
        if image is not None:
            link = image.url

        if link is None:
            await errorrespond(interaction, "No media provided")
            return

        await interaction.response.defer()
        try:
            out = caption(link, text, silent=False)
            await interaction.followup.send(text, file=discord.File(out))
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)))
        


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CaptionCog(bot), guild=labowor)
