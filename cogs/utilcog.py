from dis import disco
from random import choice
import discord
from discord import app_commands
from discord.ext import commands

from util.msgutil import devcheck


class UtilCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="status", description="set the bot's status")
    @app_commands.choices(
        status=[
            app_commands.Choice(name="🟢", value="online"),
            app_commands.Choice(name="🟡", value="idle"),
            app_commands.Choice(name="🔴", value="dnd"),
        ],
        activity=[
            app_commands.Choice(name="Playing", value="playing"),
            app_commands.Choice(name="Streaming", value="streaming"),
            app_commands.Choice(name="Listening to", value="listening"),
            app_commands.Choice(name="Watching", value="watching"),
            app_commands.Choice(name="Custom", value="custom"),
            app_commands.Choice(name="Competing in", value="competing"),
        ]
    )
    async def setstatus(self, interaction: discord.Interaction, status: app_commands.Choice[str] = "online", activity: app_commands.Choice[str] = "custom", text: str = None):
        if not await devcheck(interaction):
            return

        if text is None:
            await self.bot.change_presence()
            await interaction.response.send_message("Status cleared", ephemeral=True)
        else:
            statusdict = {
                "online": discord.Status.online,
                "idle": discord.Status.idle,
                "dnd": discord.Status.do_not_disturb,
            }

            activitydict = {
                "playing": discord.Game(text),
                "streaming": discord.Activity(type=discord.ActivityType.streaming, name=text),
                "listening": discord.Activity(type=discord.ActivityType.listening, name=text),
                "watching": discord.Activity(type=discord.ActivityType.watching, name=text),
                "custom": discord.CustomActivity(name=text),
                "competing": discord.Activity(type=discord.ActivityType.competing, name=text)
            }

            await self.bot.change_presence(
                activity=activitydict[activity.value], status=statusdict[status.value]
            )

            content = f"Status set to {status.name}:\n"
            if activity.value != "custom":
                content += f"**{activity.name}** "
            content += text

            await interaction.response.send_message(content=content, ephemeral=True)

    # purge her own messages
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @app_commands.command(name="purr", description="purge her own messages")
    @app_commands.describe(limit="number of messages to fetch")
    async def purge_self(self, interaction: discord.Interaction, limit: int):
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer()

        deleted = await interaction.channel.purge(
            limit=limit, check=lambda message: message.author.id == self.bot.user.id
        )
        await interaction.followup.send(
            f"Purrged {len(deleted)} messages", ephemeral=True
        )
    
    # force shutdown
    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="shutdown", description="shut down the app")
    async def shutdown(self, interaction: discord.Interaction):
        if not await devcheck(interaction):
            return
        await interaction.response.send_message("Shutting down...", ephemeral=True)
        try:
            await self.bot.http.close()
            await self.bot.close()
        except Exception as e:
            print(e)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UtilCog(bot))
