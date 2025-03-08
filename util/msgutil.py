import discord
from util.const import dev
import re
from discord.utils import escape_markdown

from util.loghelper import log

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
        log.warning(f"Unauthorized access from {interaction.user.mention} {interaction.user.name}")
        await errorrespond(interaction, f"Only <@{dev}> is allowed to use this command")
        return False

def escape_markdown_extra(text: str, unembed_liks = False) -> str:
    # TODO: test order of operations
    text = escape_markdown(text)

    if unembed_liks:
        text = re.sub(r"<(https?://\S+)>", r"\1", text)
    
    return text