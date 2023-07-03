import requests
import discord
from discord_webhook import DiscordWebhook

from urlparser import download, downloadpath

# base header so that we dont get 403
pixiv_baseheader = lambda x : {"referer": f"https://www.pixiv.net/member_illust.php?mode=medium&illust_id={x}"}

# fetch info from id
class PixivPost:
    def __init__(self, postid: int):
        artwork = requests.get(f"https://www.pixiv.net/ajax/illust/{postid}").json()["body"]
        self.artist = artwork["userName"]
        self.id = postid
        self.imgurl = artwork["urls"]["original"]
        self.imgext = artwork["urls"]["original"].split(".")[-1]
        self.filename = f"{self.artist}_{self.id}.{self.imgext}"


# downloads a pixiv link
def pixiv_download(link: str):
    # get post
    pixpost = PixivPost(int(link.split("/")[-1]))

    # download in artist_postid.ext format
    download(pixpost.imgurl, downloadpath, pixpost.filename, headers=pixiv_baseheader(pixpost.id))
    
    # generate embed
    embed = discord.Embed(title=f"Post downloaded", url=link, color=0x0097FA)
    embed.set_thumbnail(url=f"https://embed.pixiv.net/artwork.php?illust_id={pixpost.id}")
    embed.set_footer(text=f"{downloadpath}{pixpost.filename}")
    return embed


# pixiv markdown for webhook
def pixiv_markdown(link:str, webhook: DiscordWebhook):
    # get post
    pixpost = PixivPost(int(link.split("/")[-1]))
    
    # set artists name
    webhook.content = f'[{pixpost.artist} on Pixiv](<{link}>)'
    
    # funnly little trick
    response = requests.get(pixpost.imgurl, headers=pixiv_baseheader(pixpost.id))
    webhook.add_file(file=response.content, filename=pixpost.filename)
