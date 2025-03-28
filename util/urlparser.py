import requests
import os
from discord import Embed
from util.const import downloadpath


# downloads an image by link, saves to path as filename
def download(link, path, filename, **kwargs):
    with open(path + filename, "wb") as img_file:
        content = requests.get(link, **kwargs).content
        if len(content) == 0:
            raise Exception("Image not found")
        img_file.write(content)


# generic url cleaner
def cleanurl(url: str):
    split = url.split("?")[0]
    return split[:-1] if split[-1] == "/" else split


# generic embed for downloads
def downloadembed(url: str, imgurl: str, filename: str):
    embed = Embed(title="Image downloaded", url=url, color=0x009AFE)
    embed.add_field(
        name=filename,
        value=f"{round(os.path.getsize(downloadpath + filename)/1024, 1)} KB",
    )
    embed.set_image(url=imgurl)
    embed.set_footer(text=downloadpath)
    return embed
