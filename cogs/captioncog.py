import discord
from discord import app_commands
from discord.ext import commands

import io

from util.msgutil import devcheck, errorembed, errorrespond

import caption.captionredux
import neptunfej.generate 

class CaptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    # caption gifs and stuff
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="caption", description="caption media")
    async def captioning(self, interaction: discord.Interaction, link: str = None, text: str = "forgot the caption", file: discord.Attachment = None, force_gif: bool = False, gif_transparency: bool = False, echo: bool = False) -> None:
        if not await devcheck(interaction):
            return
        
        if file is not None:
            link = file.url

        if link is None:
            await errorrespond(interaction, "No media provided")
            return

        await interaction.response.defer()
        try:
            out = caption.captionredux.caption(link, text, force_gif, gif_transparency)
            await interaction.followup.send(text if echo else None, file=discord.File(out))
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)))

    # neptunfej
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="neptun", description="/pa")
    async def neptun(self, interaction: discord.Interaction, text: str = "forgot the caption", reverse: bool = False) -> None:
        # what could go wrong letting people use this command :clueless:
        await interaction.response.defer()
        try:
            with io.BytesIO() as image_binary:
                neptunfej.generate.neptunfej(text, 2, (10, 10), reverse).save(image_binary, "png")
                image_binary.seek(0)
                await interaction.followup.send(file=discord.File(image_binary, "neptun.png"))
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)))
        


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CaptionCog(bot))
