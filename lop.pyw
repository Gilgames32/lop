# set working directory
import os
import sys
os.chdir(sys.path[0])

import discord
from discord.ext import commands
from discord import Activity, Status, app_commands
from dotenv import load_dotenv
import feedparser
from pysaucenao import SauceNao
from discord_webhook import DiscordWebhook

from urlparser import downloadpath
from artstash import anydownload, anymkwebhook
from jsonmng import loadjson, savejson


# init
load_dotenv()
# debug
conf = loadjson("conf")
LOPDEBUG = conf["debug"]

# ids
dev = conf["dev"]
labowor = discord.Object(id=conf["labowor"])
tostash_chid = conf["tostash"]
tomarkdown_chid = conf["tomarkdown"]
# tokens
webhookurl = os.getenv("WEBHOOK32")
sauceapi = SauceNao(api_key=os.getenv("SAUCETOKEN"))
# debug channel overwrites
if LOPDEBUG:
    # instead of #floof it will listen to #test
    webhookurl = os.getenv("WEBHOOK_DEBUG")
    tomarkdown_chid = conf["tomarkdown_debug"]

# discord init
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", description="A bot by Gil", intents=intents)


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
    await bot.tree.sync(guild=labowor)
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


# return uniform embed for errors
def errorembed(error: str):
    embed = discord.Embed(color=0xFF6700)
    embed.add_field(name="Error", value=error, inline=False)
    return embed


# respond to an interaction with uniform embeds
async def errorrespond(interaction: discord.Interaction, error: str):
    await interaction.response.send_message(embed=errorembed(error), ephemeral=True)


# gets attachment urls and embed urls from a message
def getattachmenturls(message: discord.Message):
    piclinks = []
    if message.attachments:
        for att in message.attachments:
            piclinks.append(att.url)
    if message.embeds:
        for emb in message.embeds:
            piclinks.append(emb.url)
    return piclinks


# checks if user is eligible for the interaction
async def devcheck(interaction: discord.Interaction):
    if interaction.user.id == dev:
        return True
    else:
        await errorrespond(interaction, f"Only <@{dev}> is allowed to use this command")
        return False


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


# fancy downloader, sets filenames to artist names so that i dont have to
@bot.tree.context_menu(name="Down", guild=labowor)
async def ctxdown(interaction: discord.Interaction, message: discord.Message):
    if not await devcheck(interaction):
        return
    embed = await anydownload(message.content)
    if embed is None:
        embed = errorembed(
            "The message must start with a valid link\n"
            "Currently supported sites: twitter, e621, e926, pixiv, reddit"
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# bulk download downloadables from channel history
@bot.tree.command(name="stash", description="Bulk download old messages", guild=labowor)
@app_commands.describe(count="amount of messages processed")
async def download_history(interaction: discord.Interaction, count: int):
    if not await devcheck(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    dlcount = 0
    async for message in interaction.channel.history(limit=count):
        if message.author.bot:
            continue
        embed = anydownload(message.content)
        if embed is not None:
            dlcount += 1
            await message.add_reaction("🔽")

    embed = discord.Embed(title=f"Downloaded {dlcount} posts", color=0x009AFE)
    embed.set_footer(text=downloadpath)
    await interaction.edit_original_response(embed=embed)


# purge her own messages
@bot.tree.command(name="purr", description="Purge her own messages", guild=labowor)
async def purge_self(interaction: discord.Interaction, limit: int):
    if not await devcheck(interaction):
            return
    deleted = await interaction.channel.purge(limit=limit, check=lambda message: message.author.id == bot.user.id)
    await interaction.response.send_message(f"Purrged {deleted} messages", ephemeral=True)


# on message
@bot.event
async def on_message(message: discord.Message):
    # ignore bots
    if message.author.bot:
        return

    # auto download from #to-stash
    if message.channel.id == tostash_chid:
        embed = await anydownload(message.content)
        if embed is not None:
            await message.delete()
            await message.channel.send(embed=embed, delete_after=(30*60))

    # turn twitter and e6 links to better markdowns using webhooks
    elif message.channel.id == tomarkdown_chid:
        firstlink = message.content.split(" ")[0]

        webhook = DiscordWebhook(
            url=webhookurl,
            content="",
            avatar_url=message.author.avatar.url,
            username=message.author.display_name,
        )

        if await anymkwebhook(firstlink, webhook):
            webhook.execute()
            await message.delete()


bot.run(os.getenv("LOPTOKEN"))
