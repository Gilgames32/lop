from discord import *
from discord.ext import commands

intents = Intents.all()
client = commands.Bot(self_bot=True, command_prefix="_", intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print(f"{round(client.latency * 100)}ms")
    await savestickers()


async def saveemotes():
    for server in client.guilds:
        check = input(f"check in {server.name}? ")
        if check == "yes":
            emotelist = server.emojis
            for emo in emotelist:
                if emo.animated:
                    await emo.url_as().save(f"./manual_emotes/{emo.name}.gif")
                else:
                    await emo.url_as().save(f"./manual_emotes/{emo.name}.png")


async def savestickers():
    for server in client.guilds:
        check = input(f"check in {server.name}? ")
        if check == "yes":
            stickerlist = server.stickers
            for sti in stickerlist:
                await sti.image_url().save(f"./manual_emotes/{sti.name}.{sti.format}")


client.run("USERTOKEN", bot=False)
