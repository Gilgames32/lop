import requests
import discord
import e621
import os
from dotenv import load_dotenv

# init
load_dotenv()
esix = e621.E621(("kapucni", os.getenv("E621TOKEN")))

downloadpath = "C:/GIL/Down/"
with open("./downloadpath.txt", "r") as f:
    downloadpath = f.read()


# downloads an image by link, saves to path as filename
def download(link, path, filename):
    with open(path + filename, "wb") as img_file:
        img_file.write(requests.get(link).content)


# parses an e6 or e9 link
def esix_linkparse(elink: str):
    elink = elink.split("?")[0]
    hosts = ["e621", "e926"]
    for h in hosts:
        if elink.startswith(f"https://{h}.net/posts/"):
            return elink
    else:
        return None


# return the epost
def esix_getpost(elink: str):
    eid = int(elink.split("/")[4])
    epost = esix.posts.get(eid)
    if "conditional_dnp" in epost.tags.artist:
        epost.tags.artist.remove("conditional_dnp")
    return epost


# downloads an e6 or e9 link
def esix_download(link: str):
    elink = esix_linkparse(link)
    if elink is None:
        return None
    epost = esix_getpost(elink)
    # artist_postid.ext format
    filename = f"{epost.tags.artist[0]}_{epost.id}.{epost.file.ext}"
    download(epost.file.url, downloadpath, filename)
    embed = discord.Embed(title=f"Post downloaded", url=elink, color=0x012E56)
    embed.set_thumbnail(url=epost.file.url)
    embed.set_footer(text=f"{downloadpath}{filename}")
    return embed


# esix markdown for webhook
def esix_markdown(link: str):
    elink = esix_linkparse(link)
    if elink is None:
        return None
    epost = esix_getpost(elink)
    if epost.rating == "s":
        elink = elink.replace("e621", "e926")
    return (
        f'[{epost.tags.artist[0]} on {"E926" if epost.rating == "s" else "E621"}](<{elink}>)'
        + f' [{"-" if epost.file.ext == "png" else "~"}]({epost.file.url})'
    )


# parse url if twitter is in it
def tw_linkparse(twlink: str):
    twlink = twlink.split("?")[0]
    hosts = ["twitter", "fxtwitter", "vxtwitter"]
    for h in hosts:
        if twlink.startswith(f"https://{h}.com/"):
            return twlink.replace(h, "d.fxtwitter")
    else:
        return None


# returns a list of image urls of the gallery
def tw_gallery(fxlink: str):
    links = [requests.get(fxlink).url]
    for i in range(1, 4):
        responseurl = requests.get(f"{fxlink}/photo/{i+1}").url
        if responseurl == links[0]:
            break
        else:
            links.append(responseurl.split("?")[0])
    return links


# dowload from twitter
def tw_download(twlink: str):
    dfxlink = tw_linkparse(twlink)
    if dfxlink is None:
        return None

    gallery = tw_gallery(dfxlink)
    for i, glink in enumerate(gallery):
        # artist_postid_gidx.ext
        filename = f'{twlink.split("/")[3].lower()}_{twlink.split("/")[5]}{"_"+str(i) if len(gallery) > 1 else ""}.{glink.split(".")[-1]}'
        download(glink, downloadpath, filename)

    embed = discord.Embed(title=f"Tweet downloaded", url=twlink, color=0x1D9BF0)
    embed.set_thumbnail(url=dfxlink)
    embed.set_footer(text=downloadpath + filename)
    return embed


# twitter link to markdown message for webhook
def tw_markdown(link: str):
    fxlink = tw_linkparse(link)
    if fxlink is None:
        return None
    content = f'[{link.split("/")[3]} on Twitter](<{link}>)'
    gallery = tw_gallery(fxlink)
    for glink in gallery:
        content += f' [{"-" if glink.split(".")[-1] == "png" else "~"}]({glink})'
    return content


# try every existing download method
def trydownloadall(content: str):
    content = content.split(" ")[0].split("?")[0]
    embed = None
    if "twitter" in content:
        embed = tw_download(content)
    elif "e926" in content or "e621" in content:
        embed = esix_download(content)
    return embed
