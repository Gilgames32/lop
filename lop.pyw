# set working directory
import os
import sys

from util.loghelper import LOGSPATH, log, log_command

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
    await bot.start(os.getenv("LOPTOKEN"))


# on ready
@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")
    if LOPDEBUG:
        log.debug("Debug mode enabled")


# manual sync
# descriptions should follow the "This description will..." format
@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="sync", description="sync the command tree")
async def sync_cmd(interaction: discord.Interaction):
    log_command(interaction)
    if not await devcheck(interaction):
        return
    await interaction.response.defer(ephemeral=True)
    await bot.tree.sync()
    await interaction.followup.send("Command tree synced")


@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="logs", description="get the latest logs")
async def get_logs(interaction: discord.Interaction):
    log_command(interaction)
    if not await devcheck(interaction):
        return
    
    await interaction.response.defer(ephemeral=True)
    
    if not os.path.exists(LOGSPATH):
        await interaction.followup.send("No logs found")
    
    wall_of_logs = ""
    with open(LOGSPATH, "r") as f:
        for log in reversed(f.readlines()):
            if len(wall_of_logs) + len(log) > 1984:
                break
            wall_of_logs = log + wall_of_logs

    await interaction.followup.send(f"```{wall_of_logs}```")



asyncio.run(main())
