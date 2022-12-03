# https://guide.pycord.dev/interactions/
import discord
import os
from dotenv import load_dotenv
from pysaucenao import SauceNao
from todoist_api_python.api_async import TodoistAPIAsync


load_dotenv()
bot = discord.Bot(debug_guilds=[834100481839726693])
dev = 954419840251199579
sauceapi = SauceNao(api_key=os.getenv("SAUCETOKEN"))
todoapi = TodoistAPIAsync(os.getenv("TODOISTTOKEN"))
todo_inbox = "2262995514"
todo_dcsection = "103174395"


async def errorrespond(ctx, error):
    embed = discord.Embed(color=0x5865f2)
    embed.add_field(name="Error", value=error, inline=False)
    await ctx.respond(embed=embed, ephemeral=True)


def getattachmenturls(message):
    piclinks = []
    if message.attachments:
        for att in message.attachments:
            piclinks.append(att.url)
    if message.embeds:
        for emb in message.embeds:
            piclinks.append(emb.url)
    return piclinks


@bot.event
async def on_ready():
    print(f"{bot.user} reports for a moderate amount trolling")


@bot.message_command(name="SauceNAO")
async def saucefind(ctx, message: discord.Message):
    piclinks = getattachmenturls(message)

    if len(piclinks) == 1:
        try:
            results = await sauceapi.from_url(piclinks[0])
        except Exception as error:
            await errorrespond(ctx, "Something went wrong")
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
            await ctx.respond(embed=embed, ephemeral=True)

        else:
            await errorrespond(ctx, "Sauce not found")

    else:
        await errorrespond(ctx, "The message must contain one and only one attachment")


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


@bot.message_command(name="Search image links")
async def imagesearch(ctx, message: discord.Message):
    piclinks = getattachmenturls(message)

    if len(piclinks) == 1:
        await ctx.respond(view=SIButtons(piclinks[0]), ephemeral=True)

    else:
        await errorrespond(ctx, "The message must contain one and only one attachment")


@bot.message_command(name="Add task")
async def todoaddtask(ctx, message: discord.Message):
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

        await ctx.respond(embed=embed, ephemeral=True)

    except Exception as error:
        await errorrespond(ctx, "Failed to add task")
        print(error)


bot.run(os.getenv("LOPTOKEN"))
