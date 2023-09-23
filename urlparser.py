import requests
import os
import json
from discord import Embed

downloadpath = "C:/GIL/Down/"
with open("./downloadpath.txt", "r") as f:
    downloadpath = f.read()


# save jsons
def savejson(jsonname: str, jdata):
    with open(f"{jsonname}.json", "w+") as outpoot:
        json.dump(jdata, outpoot, sort_keys=True, indent=4)


# load jsons
def loadjson(jsonname: str):
    with open(f"{jsonname}.json", "r") as inpoot:
        return json.load(inpoot)


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
def anyembed(url: str, imgurl: str, filename: str):
    embed = Embed(title="Image downloaded", url=url, color=0x009AFE)
    embed.add_field(name=filename, value=f"{round(os.path.getsize(downloadpath + filename)/1024, 1)} KB")
    embed.set_image(url=imgurl)
    embed.set_footer(text=downloadpath)
    return embed
