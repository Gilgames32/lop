import discord
from discord_webhook import DiscordWebhook
import e621
import os
from dotenv import load_dotenv

from urlparser import downloadpath, download


# init
load_dotenv()
esix = e621.E621(("kapucni", os.getenv("E621TOKEN")))


# return the epost, preprocess artists
def esix_getpost(elink: str):
    # get id
    eid = int(elink.split("/")[4])
    
    # fetch post
    epost = esix.posts.get(eid)
    
    # remove conditional dnp from artists
    if "conditional_dnp" in epost.tags.artist:
        epost.tags.artist.remove("conditional_dnp")

    # if it really has no artist
    if epost.tags.artist == []:
        epost.tags.artist.append("unknown")
    
    return epost


# downloads an e6 or e9 link
def esix_download(link: str):
    # get post
    epost = esix_getpost(link)
    
    # download in artist_postid.ext format
    filename = f"{epost.tags.artist[0]}_{epost.id}.{epost.file.ext}"
    download(epost.file.url, downloadpath, filename)

    # generate embed
    embed = discord.Embed(title=f"Post downloaded", url=link, color=0x012E56)
    embed.set_thumbnail(url=epost.file.url)
    embed.set_footer(text=f"{downloadpath}{filename}")
    return embed


# esix markdown for webhook
def esix_markdown(link:str, webhook: DiscordWebhook):
    # get post
    epost = esix_getpost(link)
    
    # switch to e9 if the rating is safe
    if epost.rating == "s":
        link = link.replace("e621", "e926")
    
    # modify content
    webhook.content = f'[{epost.tags.artist[0]} on {"E926" if epost.rating == "s" else "E621"}](<{link}>)' \
                    + f' [{"-" if epost.file.ext == "png" else "~"}]({epost.file.url})'