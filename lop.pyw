import os
import discord
from discord import app_commands
from dotenv import load_dotenv
import feedparser
from pysaucenao import SauceNao
from discord_webhook import DiscordWebhook

from urlparser import downloadpath
from artstash import anydownload, anymkwebhook

# init
load_dotenv()

# keys
labowor = discord.Object(id=834100481839726693)
webhookurl = os.getenv("WEBHOOK32")
dev = 954419840251199579
sauceapi = SauceNao(api_key=os.getenv("SAUCETOKEN"))
stash_chid = 1113025678632300605
twmrkdown_chid = 969498055151865907


# discord init
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# sync command tree, currently disabled, syncing is manual
@client.event
async def setup_hook():
    # await tree.sync(guild=labowor)
    print("Command tree syncing is recommended")


# manual sync
@tree.command(name="sync", description="Sync the command tree", guild=labowor)
async def sync_cmd(interaction: discord.Interaction):
    await tree.sync(guild=labowor)
    await interaction.response.send_message("Command tree synced", ephemeral=True)


# on ready
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


# return uniform embed for errors
def errorembed(error: str):
    embed = discord.Embed(color=0x5865F2)
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
@tree.command(name="panik", description="Shut down the app", guild=labowor)
async def panic(interaction: discord.Interaction):
    if not await devcheck(interaction):
        return
    await interaction.response.send_message(view=Panik(), ephemeral=False)


# debug ping, also sets the status, snowflake
@tree.command(name="debug", description="Debug ping", guild=labowor)
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(":3")
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="Gil's nightmares"
        )
    )


# rss feedparse for twokinds
@tree.command(name="twokinds", description="Sends latest TwoKinds page", guild=labowor)
async def twokinds(interaction: discord.Interaction):
    tkfeed = feedparser.parse("https://twokinds.keenspot.com/feed.xml")
    newpagelink = tkfeed.entries[0]["links"][0]["href"]
    await interaction.response.send_message(newpagelink)


# reverse image search with saucenao
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
@tree.context_menu(name="Down", guild=labowor)
async def ctxdown(interaction: discord.Interaction, message: discord.Message):
    if not await devcheck(interaction):
        return
    embed = anydownload(message.content)
    if embed is None:
        embed = errorembed(
            "The message must start with a valid link\n"
            "Currently supported sites: twitter, e621, e926, pixiv"
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


# bulk download downloadables from channel history
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
        embed = anydownload(message.content)
        if embed is not None:
            dlcount += 1
            await message.add_reaction("🔽")

    embed = discord.Embed(title=f"Downloaded {dlcount} posts", color=0x5865F2)
    embed.set_footer(text=downloadpath)
    await interaction.edit_original_response(embed=embed)


# on message
@client.event
async def on_message(message: discord.Message):
    # ignore bots
    if message.author.bot:
        return

    # auto download from #to-stash
    if message.channel.id == stash_chid:
        embed = anydownload(message.content)
        if embed is not None:
            await message.delete()
            await message.channel.send(embed=embed, delete_after=30)

    # turn twitter and e6 links to better markdowns using webhooks
    elif message.channel.id == twmrkdown_chid:
        firstlink = message.content.split(" ")[0]

        webhook = DiscordWebhook(
            url=webhookurl,
            content="",
            avatar_url=message.author.avatar.url,
            username=message.author.display_name,
        )

        if anymkwebhook(firstlink, webhook):
            await message.delete()
            webhook.execute()


client.run(os.getenv("LOPTOKEN"))
