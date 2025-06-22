import discord
from discord import app_commands
from discord.ext import commands

from util.const import *
from util.loghelper import log_cog_load, log_command
from util.msgutil import *
from posts.supported import anypost
from util.whook import threadhook_send
from util.urlparser import downloadpath


class StashCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        log_cog_load(self)

    
    # twitter markdown with extra steps
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @app_commands.command(name="impersonate", description="send twitter as markdown")
    async def impersonate(
        self, interaction: discord.Interaction, link: str, impersonate: bool = True
    ):
        log_command(interaction)
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)

        try:
            post = anypost(link)
            await post.fetch()
            await threadhook_send(interaction.channel, self.bot, post.get_message(impersonate), post.get_username(), post.get_avatar())
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)[:2000]))
        
        await interaction.followup.send("✅", ephemeral=True)


    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="fx", description="fix embeds")
    async def fx(self, interaction: discord.Interaction, link: str, short: bool = False):
        log_command(interaction)
        await interaction.response.defer()

        try:
            post = anypost(link)
            await post.fetch()
            if short:
                await interaction.followup.send(post.get_short_message(True))
            else:
                await interaction.followup.send(post.get_message(True))
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)[:2000]))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore bots
        if message.author.bot:
            return

        # auto download from #to-stash
        if message.channel.id == tostash_chid:
            firstlink = message.content.split(" ")[0]
            post = anypost(firstlink)
            if not post:
                return
            
            try:
                await post.fetch()
                embed = post.download(downloadpath)
                await message.delete()
                await message.channel.send(embed=embed, delete_after=(30 * 60))
            except Exception:
                pass

        # embed to markdown
        else:
            firstlink = message.content.split(" ")[0]
            post = anypost(firstlink)
            if not post:
                return

            try:
                await post.fetch()
                await threadhook_send(message.channel, self.bot, post.get_message(True), message.author.display_name, message.author.display_avatar)
                await message.delete()
            except Exception:
                pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StashCog(bot))
