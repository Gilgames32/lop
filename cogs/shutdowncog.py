import discord
from discord import app_commands
from discord.ext import commands

from util.msgutil import devcheck


# view for panik shutdown
class Panik(discord.ui.View):
    bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        Panik.bot = bot
        super().__init__()

    @discord.ui.button(emoji="✔", style=discord.ButtonStyle.green)
    async def shutdown(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not await devcheck(interaction):
            return
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.message.delete()

        await Panik.bot.close()
        await Panik.bot.http.close()
        await Panik.bot.session.close()
        Panik.bot.loop.close()

    @discord.ui.button(emoji="✖", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await devcheck(interaction):
            return
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.message.delete()


class ShutdownCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    # force shutdown
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="panik", description="shut down the app")
    async def panic(self, interaction: discord.Interaction):
        if not await devcheck(interaction):
            return
        await interaction.response.send_message(view=Panik(self.bot), ephemeral=False)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ShutdownCog(bot))
