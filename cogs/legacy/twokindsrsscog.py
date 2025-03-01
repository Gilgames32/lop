import discord
from discord import app_commands
from discord.ext import commands

import feedparser


class TKRSSCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    # rss feedparse for twokinds
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="twokinds", description="send the latest TwoKinds page")
    async def twokinds(self, interaction: discord.Interaction):
        await interaction.response.defer()
        tkfeed = feedparser.parse("https://twokinds.keenspot.com/feed.xml")
        newpagelink = tkfeed.entries[0]["links"][0]["href"]
        await interaction.followup.send(newpagelink)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TKRSSCog(bot))
