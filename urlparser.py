import requests
import os
from discord import Embed

downloadpath = "C:/GIL/Down/"
with open("./downloadpath.txt", "r") as f:
    downloadpath = f.read()


# downloads an image by link, saves to path as filename
def download(link, path, filename, **kwargs):
    with open(path + filename, "wb") as img_file:
        img_file.write(requests.get(link, **kwargs).content)


# generic url cleaner
def cleanurl(url: str):
    return url.split("?")[0]


# generic embed for downloads
def anyembed(url: str, imgurl: str, filename: str):
    embed = Embed(title="Image downloaded", url=url, color=0x009AFE)
    embed.add_field(name=filename, value=f"{round(os.path.getsize(downloadpath + filename)/1024, 1)} KB")
    embed.set_image(url=imgurl)
    embed.set_footer(text=downloadpath)
    return embed
