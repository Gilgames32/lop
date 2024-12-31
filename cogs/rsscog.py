import discord
from discord import app_commands
from discord.ext import commands, tasks

import time

from util.const import *
from util.msgutil import *




class RSSCog(commands.GroupCog, group_name='rss'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.rss_parse_all.start()
        print("Loaded", __class__.__name__)


    @tasks.loop(hours=4)
    async def rss_parse_all(self):
        print("Parsing rss feeds")
        return
        
        before = time.time()
        after = conf["last_sync"]

        for feed_url, channels in conf["rss"].items():
            feed = anyfeed(feed_url)
            # TODO
            # fetch posts
            # post posts
            for channel in channels:
                pass
                
        
        conf["last_sync"] = before
        saveconf()

    
    @rss_parse_all.before_loop
    async def _before_loop(self):
        await self.bot.wait_until_ready()





                

    @app_commands.command(name="add", description="add an rss feed")
    async def addfeed(self, interaction: discord.Interaction, feed: str):
        if not await devcheck(interaction):
            return
        
        if feed not in conf["rss"]:
            conf["rss"][feed] = []

        if interaction.channel_id in conf["rss"][feed]:
            await interaction.response.send_message(f"Feed `{feed}` already added", ephemeral=True)
            return
        
        conf["rss"][feed].append(interaction.channel_id)
        saveconf()

        await interaction.response.send_message(f"Added `{feed}` to the feeds", ephemeral=True)
        
    
    @app_commands.command(name="remove", description="remove an rss feed")
    async def rmfeed(self, interaction: discord.Interaction, feed: str):
        if not await devcheck(interaction):
            return
        
        if feed not in conf["rss"]:
            await interaction.response.send_message(f"Feed `{feed}` not found", ephemeral=True)
            return
        
        conf["rss"][feed].remove(interaction.channel_id)
        # remove empty keys so we dont fetch them
        if not conf["rss"][feed]:
            del conf["rss"][feed]
        saveconf()

        await interaction.response.send_message(f"Removed `{feed}` from the feeds", ephemeral=True)
        
    
    @app_commands.command(name="list", description="list all feeds")
    async def lsfeeds(self, interaction: discord.Interaction):
        if not await devcheck(interaction):
            return
        
        channel_feeds = []
        for feed, channels in conf["rss"].items():
            if interaction.channel_id in channels:
                channel_feeds.append(feed)

        if not channel_feeds:
            await interaction.response.send_message("No feeds found", ephemeral=True)
        else:
            await interaction.response.send_message("\n".join(map(lambda x: f"`{x}`", channel_feeds)), ephemeral=True)

        
                


        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RSSCog(bot))