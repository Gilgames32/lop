import requests
from discord_webhook import DiscordWebhook
from urlparser import anyembed

from urlparser import download, downloadpath, cleanurl

# parse url and prepare download link
def tw_linkparse(twlink: str):
    # clean trackers
    twlink = cleanurl(twlink)

    # replace with d.fxtwitter
    hosts = ["twitter", "fxtwitter", "vxtwitter"]
    for h in hosts:
        if twlink.startswith(f"https://{h}.com/"):
            return twlink.replace(h, "d.fxtwitter")


# returns a list of image urls of the gallery
def tw_gallery(fxlink: str):
    # get the real pbs.twitter link
    links = [cleanurl(requests.get(fxlink).url)]

    # if the photo id was specified, disregard the rest
    if "/photo/" in fxlink:
        return links

    # process all images
    for i in range(1, 4):
        responseurl = cleanurl(requests.get(f"{fxlink}/photo/{i+1}").url)
        if responseurl == links[0]:
            break
        else:
            links.append(responseurl)
    
    return links


# dowload from twitter
def tw_download(twlink: str):
    # generate d.fxtwitter link
    dfxlink = tw_linkparse(twlink)

    # fetch gallery
    gallery = tw_gallery(dfxlink)
    for i, glink in enumerate(gallery):
        # download in artist_postid_gidx.ext format
        filename = f'{twlink.split("/")[3].lower()}_{twlink.split("/")[5]}{"_"+str(i) if len(gallery) > 1 else ""}.{glink.split(".")[-1]}'
        download(glink, downloadpath, filename)

    # generate embed
    return anyembed(twlink, dfxlink, filename)


# twitter markdown for webhook
def tw_markdown(link:str, webhook: DiscordWebhook):
    # generate d.fxtwitter link
    dfxlink = tw_linkparse(link)
    
    # fetch gallery
    gallery = tw_gallery(dfxlink)
    
    # setup content
    content = f'[{link.split("/")[3]} on Twitter](<{link}>)'

    # add multiple posts if needed
    for glink in gallery:
        content += f' [{"-" if glink.split(".")[-1] == "png" else "~"}]({glink})'
    
    # modify content
    webhook.content = content