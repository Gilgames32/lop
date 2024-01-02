import discord
from discord import app_commands
from discord.ext import commands

import json
import os
from util.const import labowor, savejson, loadjson
from util.msgutil import devcheck, errorrespond


class GifSyncCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    # sync gifs to cloud
    @app_commands.command(
        name="gifsync", description="Sync favorite gifs with the cloud"
    )
    @app_commands.describe(gc="gif collection json")
    async def purge_self(
        self, interaction: discord.Interaction, gc: discord.Attachment = None
    ):
        if not await devcheck(interaction):
            return

        # check if cloud save exists
        if not os.path.exists("./gif-collections.json"):
            savejson("gif-collections", {})

        # check sync direction
        if gc is None:
            await interaction.response.send_message(
                f"Unfinished feature",
                ephemeral=True,
                file=discord.File("./gif-collections.json"),
            )

        # json check
        if not gc.filename.endswith(".json"):
            await errorrespond(interaction, "File must be a json")
            return

        # load cloud save
        # TODO merge the two instead of replacing
        await gc.save("./gif-collections.json")
        await interaction.response.send_message(
            f"Unfinished feature\nCloud save overwritten", ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GifSyncCog(bot), guild=labowor)
