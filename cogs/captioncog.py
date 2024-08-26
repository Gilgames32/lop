import discord
from discord import app_commands
from discord.ext import commands

from util.msgutil import devcheck, errorembed, errorrespond

from caption.src.pipeline import caption

class CaptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    # caption gifs and stuff
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="caption", description="caption media")
    async def captioning(self, interaction: discord.Interaction, link: str = None, text: str = "forgot the caption", image: discord.Attachment = None, force_gif: bool = False, gif_transparency: bool = False) -> None:
        if not await devcheck(interaction):
            return
        
        if image is not None:
            link = image.url

        if link is None:
            await errorrespond(interaction, "No media provided")
            return

        await interaction.response.defer()
        try:
            out = caption(link, text, force_gif, gif_transparency)
            await interaction.followup.send(text, file=discord.File(out))
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)))
        


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CaptionCog(bot))
