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

# followup an interaction with uniform embeds
async def errorfollowup(interaction: discord.Interaction, error: str):
    await interaction.followup.send(embed=errorembed(error), ephemeral=True)


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
        text = unembed_links(text)
    
    return text

def unembed_links(text: str) -> str:
    # replace [link](link) with link
    text = re.sub(r"\[https?://[^\s\)\]]+\]\((https?://[^\s\)\]]+)\)", r"\1", text)

    # replace normal links with <link>
    text = re.sub(r"(?<!(\]\())(https?://[^\s\)\]]+)", r"<\2>", text)
    
    # replace markdown links with [](<link>)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r"[\1](<\2>)", text)
    return text

# this is utterly stupid
def truncate(text: str, max_length: int, placeholder: str = "...") -> str:
    if max_length <= 0:
        return ""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    
    max_length -= len(placeholder)
    return " ".join(text[:max_length].split(" ")[:-1]) + placeholder
