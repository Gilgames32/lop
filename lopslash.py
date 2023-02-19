# from discord_webhook import DiscordWebhook
import os
import discord
from discord import app_commands
from dotenv import load_dotenv
import feedparser
from pysaucenao import SauceNao
from todoist_api_python.api_async import TodoistAPIAsync


# init
load_dotenv()

# const
labowor = discord.Object(id=834100481839726693)
webhookurl = os.getenv("WEBHOOK32")
dev = 954419840251199579

sauceapi = SauceNao(api_key=os.getenv("SAUCETOKEN"))

todoapi = TodoistAPIAsync(os.getenv("TODOISTTOKEN"))
todo_inbox = "2262995514"
todo_dcsection = "103174395"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# UTIL
@client.event
async def setup_hook():
    # await tree.sync(guild=labowor)
    print("Command tree syncing is recommended")


@tree.command(name="sync", description="Sync the command tree", guild=labowor)
async def first_command(interaction: discord.Interaction):
    await tree.sync(guild=labowor)
    await interaction.response.send_message("Command tree synced", ephemeral=True)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


async def errorrespond(interaction: discord.Interaction, error):
    embed = discord.Embed(color=0x5865f2)
    embed.add_field(name="Error", value=error, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


def getattachmenturls(message):
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


@tree.command(name="flora", description="debug", guild=labowor)
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('Nya!')


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

    if len(piclinks) == 1:
        try:
            results = await sauceapi.from_url(piclinks[0])
        except Exception as error:
            await errorrespond(interaction, "Something went wrong")
            print(error)
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


class SIButtons(discord.ui.View):
    def __init__(self, piclink):
        super().__init__(timeout=None)
        self.piclink = piclink

        google_button = discord.ui.Button(label="Google", style=discord.ButtonStyle.link,
                                          url=f"https://www.google.com/searchbyimage?sbisrc=1&image_url={piclink}")
        saucenao_button = discord.ui.Button(label="SauceNAO", style=discord.ButtonStyle.link,
                                            url=f"https://saucenao.com/search.php?db=999&url={piclink}")
        yandex_button = discord.ui.Button(label="Yandex", style=discord.ButtonStyle.link,
                                          url=f"https://yandex.com/images/search?url={piclink}&rpt=imageview")

        self.add_item(google_button)
        self.add_item(saucenao_button)
        self.add_item(yandex_button)


# IMAGE REVERSE SEARCH LINKS
@tree.context_menu(name="Image reverse", guild=labowor)
async def imagesearch(interaction: discord.Interaction, message: discord.Message):
    piclinks = getattachmenturls(message)

    if len(piclinks) == 1:
        await interaction.response.send_message(view=SIButtons(piclinks[0]), ephemeral=True)

    else:
        await errorrespond(interaction, "The message must contain one and only one attachment")


# TODOIST IMPLEMENTATION
@tree.context_menu(name="Add task", guild=labowor)
async def todoaddtask(interaction: discord.Interaction, message: discord.Message):
    if not await devcheck(interaction):
        return

    try:
        # E44332
        embed = discord.Embed(color=0xe44332)
        desc = ""

        # ha van több sor, az első lesz a title, és minden megy descbe
        title = message.content.split("\n")[0]
        if "\n" in message.content:
            desc = message.content

        # ha embed kép
        if message.embeds:
            if message.embeds[0].type == "image":
                embed.set_thumbnail(url=message.embeds[0].url)
                # link csere fájlnévre
                if title == message.content.split("\n")[0]:
                    title = message.embeds[0].url.split("/")[-1]
                    desc = message.content

        # ha van csatolmány
        if message.attachments:
            embed.set_thumbnail(url=message.attachments[0].url)
            if title == "":
                title = message.attachments[0].url.split("/")[-1]

            for att in message.attachments:
                desc += "\n" + att.url

        embed.add_field(name="Task added", value=title, inline=True)

        await todoapi.add_task(content=title, description=desc.strip(), project_id=todo_inbox,
                               section_id=todo_dcsection)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as error:
        await errorrespond(interaction, "Failed to add task")
        print(error)


client.run(os.getenv("LOPTOKEN"))
