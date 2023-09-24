# set working directory
import os
import sys
os.chdir(sys.path[0])

from const import *
from msgutil import *

import asyncio
import discord
from discord.ext import commands
from discord import Activity, Status, app_commands
import feedparser
from discord_webhook import DiscordWebhook

from urlparser import downloadpath
from artstash import anydownload, anymkwebhook


# discord init
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", description="A bot by Gil", intents=intents)


# load cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

# startup
async def main():
    await load_cogs()
    await bot.start(os.getenv("LOPTOKEN"))


# sync command tree, currently disabled, syncing is manual
@bot.event
async def setup_hook():
    # await tree.sync(guild=labowor)
    print("Command tree syncing is recommended")


# manual sync
@bot.tree.command(name="sync", description="Sync the command tree", guild=labowor)
async def sync_cmd(interaction: discord.Interaction):
    if not await devcheck(interaction):
            return
    await bot.tree.sync(guild=interaction.guild)
    await interaction.response.send_message("Command tree synced", ephemeral=True)


# on ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if LOPDEBUG:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="Debugging"
            ), 
            status=Status.dnd
        )
        print("Status set, debug mode enabled")





# view for panik shutdown
class Panik(discord.ui.View):
    @discord.ui.button(emoji="✔", style=discord.ButtonStyle.green)
    async def shutdown(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not await devcheck(interaction):
            return
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.message.delete()
        quit()

    @discord.ui.button(emoji="✖", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await devcheck(interaction):
            return
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.message.delete()


# force shutdown
@bot.tree.command(name="panik", description="Shut down the app", guild=labowor)
async def panic(interaction: discord.Interaction):
    if not await devcheck(interaction):
        return
    await interaction.response.send_message(view=Panik(), ephemeral=False)


# debug ping, also sets the status, snowflake
@bot.tree.command(name="debug", description="Debug ping", guild=labowor)
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(":3")
    if LOPDEBUG:
        return
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="Gil's nightmares"
        )
    )


# rss feedparse for twokinds
@bot.tree.command(name="twokinds", description="Sends latest TwoKinds page", guild=labowor)
async def twokinds(interaction: discord.Interaction):
    tkfeed = feedparser.parse("https://twokinds.keenspot.com/feed.xml")
    newpagelink = tkfeed.entries[0]["links"][0]["href"]
    await interaction.response.send_message(newpagelink)


# reverse image search with saucenao
@bot.tree.context_menu(name="SauceNAO", guild=labowor)
async def saucefind(interaction: discord.Interaction, message: discord.Message):
    if not await devcheck(interaction):
        return

    piclinks = getattachmenturls(message)

    if len(piclinks) > 0:
        try:
            results = await sauceapi.from_url(piclinks[0])
        except any:
            await errorrespond(interaction, "Something went wrong")
            return

        if len(results) != 0:
            embed = discord.Embed(
                title="Sauce found",
                url=f"https://saucenao.com/search.php?db=999&url={piclinks[0]}",
                color=0x5865F2,
            )
            embed.set_thumbnail(url=results[0].thumbnail)
            for r in results:
                if r.index is not None and r.url is not None:
                    embed.add_field(
                        name=f"{r.index} | {r.similarity}%"
                        + (f" | {r.author_name}" if r.author_name is not None else ""),
                        value=f"{r.url}",
                        inline=False,
                    )

            embed.set_footer(
                text=f"limit {results.short_remaining}s {results.long_remaining}d"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            await errorrespond(interaction, "Sauce not found")

    else:
        await errorrespond(
            interaction, "The message must contain one and only one attachment"
        )




# purge her own messages
@bot.tree.command(name="purr", description="Purge her own messages", guild=labowor)
async def purge_self(interaction: discord.Interaction, limit: int):
    if not await devcheck(interaction):
            return
    deleted = await interaction.channel.purge(limit=limit, check=lambda message: message.author.id == bot.user.id)
    await interaction.response.send_message(f"Purrged {deleted} messages", ephemeral=True)


asyncio.run(main())
