import discord
from discord import app_commands
from discord.ext import commands

from util.const import *
from util.msgutil import *
from posts.supported import anypost
from util.whook import threadhook_send
from util.urlparser import downloadpath


class StashCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Stash",
            callback=self.ctxdown,
        )
        self.bot.tree.add_command(self.ctx_menu)
        print("Loaded", __class__.__name__)

    async def ctxdown(self, interaction: discord.Interaction, message: discord.Message):
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)

        # FIXME: this needs to be reworked
        embed = None
        if embed is None:
            embed = errorembed("This action is not supported yet")
        await interaction.followup.send(embed=embed, ephemeral=True)

    
    # twitter markdown with extra steps
    @app_commands.command(name="impersonate", description="send twitter as markdown")
    async def impersonate(
        self, interaction: discord.Interaction, link: str, impersonate: bool = True
    ):
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)

        post = anypost(link)
        await post.fetch()
        
        await threadhook_send(interaction.channel, self.bot, post.get_message(), post.get_username(), post.get_avatar())
        
        await interaction.followup.send("✅", ephemeral=True)

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
            
            await post.fetch()
            embed = post.download(downloadpath)

            await message.delete()
            await message.channel.send(embed=embed, delete_after=(30 * 60))

        # embed to markdown
        else:
            firstlink = message.content.split(" ")[0]
            post = anypost(firstlink)
            if not post:
                return

            await post.fetch()
            await threadhook_send(message.channel, self.bot, post.get_message(True), message.author.display_name, message.author.display_avatar)
            await message.delete()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StashCog(bot))
