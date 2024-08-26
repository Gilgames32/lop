# set working directory
import os
import sys

os.chdir(sys.path[0])

from util.const import *
from util.msgutil import *

import asyncio
import discord
from discord import app_commands
from discord.ext import commands


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
    print("Command tree syncing is recommended")
    await bot.start(os.getenv("LOPTOKEN"))


# on ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if LOPDEBUG:
        print("Debug mode enabled")


# manual sync
# descriptions should follow the "This description will..." format
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="sync", description="sync the command tree")
async def sync_cmd(interaction: discord.Interaction):
    if not await devcheck(interaction):
        return
    await interaction.response.defer(ephemeral=True)
    await bot.tree.sync()
    await interaction.followup.send("Command tree synced")


asyncio.run(main())
