import os
import logging
import discord

LOGSPATH = "logs/lop.log"
if not os.path.exists("logs"):
    os.makedirs("logs")

# logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# handlers
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOGSPATH)
file_handler.setLevel(logging.INFO)

# format
formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')

console_handler.setFormatter(formatter)
log.addHandler(console_handler)

file_handler.setFormatter(formatter)
log.addHandler(file_handler)


# NOTE: due to some typechecking magic and me not wanting to figure it out, this isnt a decorator
def log_command(interaction: discord.Interaction):
    log.info(f"{interaction.user.mention} {interaction.user.name} in {interaction.channel.mention} {interaction.channel.name} called /{interaction.command.name}")

def log_cog_load(cog):
    log.info(f"Loaded cog: {cog.__class__.__name__}")

