import discord
from discord import app_commands
from discord.ext import commands

import io
from urllib.parse import quote_plus

from util.loghelper import log_cog_load, log_command
from util.msgutil import devcheck, errorembed, errorrespond

import caption.captionredux
import neptunfej.generate 

class CaptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        log_cog_load(self)

    # caption gifs and stuff
    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="caption", description="caption media")
    async def captioning(self, interaction: discord.Interaction, link: str = None, text: str = "forgot the caption", file: discord.Attachment = None, force_gif: bool = False, gif_transparency: bool = False, echo: bool = False) -> None:
        log_command(interaction)
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
        log_command(interaction)
        await interaction.response.defer()
        try:
            with io.BytesIO() as image_binary:
                neptunfej.generate.neptunfej(text, 2, (10, 10), reverse).save(image_binary, "png")
                image_binary.seek(0)
                await interaction.followup.send(file=discord.File(image_binary, "neptun.png"))
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)))

    # minecraft achievements
    # send a random animal
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="minecraft", description="minecraft achievements")
    @app_commands.choices(
        icon=[
            app_commands.Choice(name="Grass", value=1),
            app_commands.Choice(name="Stone", value=20),
            #app_commands.Choice(name="Wooden Plank", value=21),
            app_commands.Choice(name="Crafting Table", value=13),
            app_commands.Choice(name="Furnace", value=18),
            app_commands.Choice(name="Chest", value=17),
            app_commands.Choice(name="Bed", value=9),
            app_commands.Choice(name="Coal", value=31),
            app_commands.Choice(name="Iron", value=22),
            app_commands.Choice(name="Gold", value=23),
            app_commands.Choice(name="Diamond", value=2),
            #app_commands.Choice(name="Sign", value=11),
            app_commands.Choice(name="Book", value=19),
            app_commands.Choice(name="Wooden Door", value=24),
            #app_commands.Choice(name="Iron Door", value=25),
            app_commands.Choice(name="Redstone", value=14),
            app_commands.Choice(name="Rail", value=12),
            #app_commands.Choice(name="Bow", value=33),
            #app_commands.Choice(name="Arrow", value=34),
            #app_commands.Choice(name="Iron Sword", value=32),
            app_commands.Choice(name="Diamond Sword", value=3),
            #app_commands.Choice(name="Iron Chestplate", value=35),
            app_commands.Choice(name="Diamond Chestplate", value=26),
            app_commands.Choice(name="TNT", value=6),
            #app_commands.Choice(name="Flint And Steel", value=27),
            app_commands.Choice(name="Fire", value=15),
            app_commands.Choice(name="Bucket", value=36),
            app_commands.Choice(name="Water Bucket", value=37),
            app_commands.Choice(name="Lava Bucket", value=38),
            #app_commands.Choice(name="Cookie", value=7),
            app_commands.Choice(name="Cake", value=10),
            app_commands.Choice(name="Milk Bucket", value=39),
            #app_commands.Choice(name="Creeper", value=4),
            #app_commands.Choice(name="Pig", value=5),
            #app_commands.Choice(name="Spawn Egg", value=30),
            app_commands.Choice(name="Heart", value=8),
            #app_commands.Choice(name="Cobweb", value=16),
            app_commands.Choice(name="Potion", value=28),
            #app_commands.Choice(name="Splash Potion", value=29)
        ]
    )
    async def minecraft(
        self,
        interaction: discord.Interaction,
        icon: app_commands.Choice[int] = 10,
        title: str = "Achievement Get!",
        desc: str = "The cake is a lie",
    ) -> None:
        log_command(interaction)
        await interaction.response.send_message(
            f"https://skinmc.net/achievement/{icon if isinstance(icon, int) else icon.value}/{quote_plus(title)}/{quote_plus(desc)}"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CaptionCog(bot))
