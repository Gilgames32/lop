import discord
from discord import app_commands
from discord.ext import commands

import requests
import io

from util.loghelper import log_cog_load, log_command


class RandomFoxCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        log_cog_load(self)

    # send a random fox
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="fox", description="send an image of a fox")
    async def random_fox(self, interaction: discord.Interaction):
        log_command(interaction)
        await interaction.response.defer()
        try:
            img = requests.get("https://api.tinyfox.dev/img?animal=fox").content
            await interaction.followup.send(
                file=discord.File(io.BytesIO(img), "fox.png")
            )
        except Exception as e:
            await interaction.followup.send(str(e))

    # send a random animal
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="animal", description="send an image of an animal")
    @app_commands.choices(
        animal=[
            app_commands.Choice(name="Bear", value="bear"),
            app_commands.Choice(name="Capybara", value="capy"),
            app_commands.Choice(name="Caracal", value="caracal"),
            app_commands.Choice(name="Cheetah", value="chee"),
            app_commands.Choice(name="Coyote", value="yote"),
            app_commands.Choice(name="Deer", value="bleat"),
            app_commands.Choice(name="Fox", value="fox"),
            app_commands.Choice(name="Hyena", value="yeen"),
            app_commands.Choice(name="Jaguar", value="jaguar"),
            app_commands.Choice(name="Lynx", value="lynx"),
            app_commands.Choice(name="Maned Wolf", value="mane"),
            app_commands.Choice(name="Puma", value="puma"),
            app_commands.Choice(name="Otter", value="ott"),
            app_commands.Choice(name="Manul", value="manul"),
            app_commands.Choice(name="Bunny", value="bun"),
            app_commands.Choice(name="Raccoon", value="racc"),
            app_commands.Choice(name="Red Panda", value="wah"),
            app_commands.Choice(name="Serval", value="serval"),
            app_commands.Choice(name="Snake", value="snek"),
            app_commands.Choice(name="Snow Leopard", value="snep"),
            app_commands.Choice(name="Tiger", value="tig"),
            app_commands.Choice(name="Wolf", value="woof"),
        ]
    )
    async def random_animals(self, interaction: discord.Interaction, animal: app_commands.Choice[str]):
        log_command(interaction)
        await interaction.response.defer()
        try:
            img = requests.get(f"https://api.tinyfox.dev/img?animal={animal.value}").content
            await interaction.followup.send(
                file=discord.File(io.BytesIO(img), f"{animal.value}.png")
            )
        except Exception as e:
            await interaction.followup.send(str(e))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RandomFoxCog(bot))
