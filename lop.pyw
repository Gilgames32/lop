import os
import discord
from discord import app_commands
from dotenv import load_dotenv
import feedparser
from pysaucenao import SauceNao
import requests
import e621
from discord_webhook import DiscordWebhook


# init
load_dotenv()

# keys
labowor = discord.Object(id=834100481839726693)
webhookurl = os.getenv("WEBHOOK32")
dev = 954419840251199579
sauceapi = SauceNao(api_key=os.getenv("SAUCETOKEN"))

downloadpath = "C:/GIL/Down/"
with open("./downloadpath.txt", "r") as f:
    downloadpath = f.read()

stash = 1113025678632300605
twitterformat = 969498055151865907
esix = e621.E621(("kapucni", os.getenv("E621TOKEN")))


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# UTIL
@client.event
async def setup_hook():
    # await tree.sync(guild=labowor)
    print("Command tree syncing is recommended")


@tree.command(name="sync", description="Sync the command tree", guild=labowor)
async def sync_cmd(interaction: discord.Interaction):
    await tree.sync(guild=labowor)
    await interaction.response.send_message("Command tree synced", ephemeral=True)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


def errorembed(error: str):
    embed = discord.Embed(color=0x5865f2)
    embed.add_field(name="Error", value=error, inline=False)
    return embed


async def errorrespond(interaction: discord.Interaction, error: str):
    await interaction.response.send_message(embed=errorembed(error), ephemeral=True)


def getattachmenturls(message: discord.Message):
    piclinks = []
    if message.attachments:
        for att in message.attachments:
            piclinks.append(att.url)
    if message.embeds:
        for emb in message.embeds:
            piclinks.append(emb.url)
    return piclinks


async def devcheck(interaction: discord.Interaction):
    if interaction.user.id == dev:
        return True
    else:
        await errorrespond(interaction, f"Only <@{dev}> is allowed to use this command")
        return False


class Panik(discord.ui.View):
    @discord.ui.button(emoji="✔", style=discord.ButtonStyle.green)
    async def shutdown(self, interaction: discord.Interaction, button: discord.ui.Button):
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


@tree.command(name="panic", description="Shut down the app", guild=labowor)
async def panic(interaction: discord.Interaction):
    if not await devcheck(interaction):
        return
    await interaction.response.send_message(view=Panik(), ephemeral=False)


@tree.command(name="debug", description="Debug ping", guild=labowor)
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(':3')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Gil's nightmares"))


# TWOKINDS RSS
@tree.command(name="twokinds", description="Sends latest TwoKinds page", guild=labowor)
async def twokinds(interaction: discord.Interaction):
    tkfeed = feedparser.parse("https://twokinds.keenspot.com/feed.xml")
    newpagelink = tkfeed.entries[0]["links"][0]["href"]
    await interaction.response.send_message(newpagelink)


# SAUCENAO IMPLEMENTATION
@tree.context_menu(name="SauceNAO", guild=labowor)
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
            embed = discord.Embed(title=f"Sauce found",
                                  url=f"https://saucenao.com/search.php?db=999&url={piclinks[0]}",
                                  color=0x5865f2)
            embed.set_thumbnail(url=results[0].thumbnail)
            for r in results:
                if r.index is not None and r.url is not None:
                    embed.add_field(name=f"{r.index} | {r.similarity}%"
                                         + (f" | {r.author_name}" if r.author_name is not None else ""),
                                    value=f"{r.url}",
                                    inline=False)

            embed.set_footer(text=f"limit {results.short_remaining}s {results.long_remaining}d")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            await errorrespond(interaction, "Sauce not found")

    else:
        await errorrespond(interaction, "The message must contain one and only one attachment")


# download using requests.get
def download(link, path, filename):
    with open(path+filename, "wb") as img_file:
        img_file.write(requests.get(link).content)


# ESIX DOWNLOADER
def getesixembed(message: discord.Message):
    elink = message.content.split(" ")[0].split("?")[0]
    if "posts" not in elink:
        return None
    eid = int(elink.split("/")[4])
    epost = esix.posts.get(eid)
    if "conditional_dnp" in epost.tags.artist:
        epost.tags.artist.remove("conditional_dnp")
    filename = f'{epost.tags.artist[0]}_{epost.id}.{epost.file.ext}'
    download(epost.file.url, downloadpath, filename)
    embed = discord.Embed(title=f"Post downloaded", url=elink, color=0x012E56)
    embed.set_thumbnail(url=epost.file.url)
    embed.set_footer(text=f'{downloadpath}{filename}')
    return embed


# parse url if twitter is in it
def twlinkparse(twlink: str):
    hosts = ["twitter", "fxtwitter", "vxtwitter"]
    for h in hosts:
        if twlink.startswith(f"https://{h}.com/"):
            return twlink.replace(h, "d.fxtwitter")
    else:
        return None

def twgallery(fxlink:str):
    links = [requests.get(fxlink).url]
    for i in range(1, 4):
        responseurl = requests.get(f'{fxlink}/photo/{i+1}').url
        if responseurl == links[0]:
            break
        else:
            links.append(responseurl)
    return links

# TWITTER DOWNLOADER
def getfxembed(message: discord.Message):
    try:
        twlink = message.content.split(" ")[0].split("?")[0]
        fxlink = twlinkparse(twlink)
        if fxlink is None:
            return

        response = requests.get(fxlink)
        filename = f'{twlink.split("/")[3].lower()}_{twlink.split("/")[5]}.{response.url.split(".")[-1]}'
        with open(downloadpath + filename, "wb") as img_file:
            img_file.write(response.content)
        embed = discord.Embed(title=f"Tweet downloaded", url=twlink, color=0x1d9bf0)
        embed.set_thumbnail(url=fxlink)
        embed.set_footer(text=downloadpath + filename)
        return embed
    except any:
        return None


# FETCHING EVERY DOWNLOADER
def trydownloadall(message: discord.Message):
    embed = None
    if "twitter" in message.content:
        embed = getfxembed(message)
    elif "e926" in message.content or "e621" in message.content:
        embed = getesixembed(message)
    return embed


# CONTEXT MENU DOWNLOADER
@tree.context_menu(name="Down", guild=labowor)
async def ctxdown(interaction: discord.Interaction, message: discord.Message):
    if not await devcheck(interaction):
        return
    embed = trydownloadall(message)
    if embed is None:
        embed = errorembed("The message must start with a valid link\n"
                           "Currently supported sites: twitter, e621, e926")
    await interaction.response.send_message(embed=embed, ephemeral=True)


# DOWNLOAD HISTORY
@tree.command(name="stash", description="Bulk download old messages", guild=labowor)
@app_commands.describe(count="amount of messages processed")
async def download_history(interaction: discord.Interaction, count: int):
    if not await devcheck(interaction):
        return

    await interaction.response.defer(ephemeral=True)

    dlcount = 0
    async for message in interaction.channel.history(limit=count):
        if message.author.bot:
            continue
        embed = trydownloadall(message)
        if embed is not None:
            dlcount += 1
            await message.add_reaction("🔽")

    embed = discord.Embed(title=f"Downloaded {dlcount} images", color=0x5865f2)
    embed.set_footer(text=downloadpath)
    await interaction.edit_original_response(embed=embed)


# ON MESSAGE
@client.event
async def on_message(message: discord.Message):
    # ignore bots
    if message.author.bot:
        return

    # AUTO DOWNLOAD FROM #to-stash
    if message.channel.id == stash:
        embed = trydownloadall(message)
        if embed is not None:
            await message.delete()
            await message.channel.send(embed=embed, delete_after=30)

    # MARKDOWN FORMAT TWITTER
    elif message.channel.id == twitterformat:
        twlink = message.content.split(" ")[0].split("?")[0]
        fxlink = twlinkparse(twlink)
        if fxlink is not None:
            content = f'[{twlink.split("/")[3]} on Twitter](<{twlink}>)'
            gallery = twgallery(fxlink)
            for link in gallery:
                content += f' [{"-" if link.split(".")[-1] == "png" else "~"}]({link})'

            webhook = DiscordWebhook(url=webhookurl, 
                                     content=content, 
                                     avatar_url=message.author.avatar.url, 
                                     username=message.author.name)
            webhook.execute()
            await message.delete()

client.run(os.getenv("LOPTOKEN"))
