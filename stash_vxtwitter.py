import requests
from discord_webhook import DiscordWebhook
from urlparser import anyembed

from urlparser import download, downloadpath, cleanurl

# temporary fix because fuck you elon
# returns a json with the info of the given tweet
def vx_jsonget(twlink: str):
    # clean trackers
    twlink = cleanurl(twlink)
    splittwlink = twlink.split("/")

    # if the photo was specified
    photo = 0
    if len(splittwlink) > 6:
        photo = int(splittwlink[-1])
        twlink = "/".join(splittwlink[:-2])

    # replace with api.vxtwitter
    hosts = ["twitter.com", "fxtwitter.com", "vxtwitter.com", "x.com"]
    for h in hosts:
        if twlink.startswith(f"https://{h}/"):
            twlink = twlink.replace(h, "api.vxtwitter.com")
            break
    
    # getting json
    vxjson = requests.get(twlink).json()
    
    # if the photo id was specified, disregard the rest
    if photo != 0:
        vxjson["mediaURLs"] = [ vxjson["mediaURLs"][photo-1] ]

    return vxjson


# dowload from twitter
async def tw_download(twlink: str):
    # get json from vxtwitter
    vxjson = vx_jsonget(twlink)

    # get gallery
    gallery = vxjson["mediaURLs"]
    for i, glink in enumerate(gallery):
        # download in artist_postid_gidx.ext format
        filename = f'{vxjson["user_screen_name"]}_{vxjson["tweetID"]}{"_"+str(i) if len(gallery) > 1 else ""}.{glink.split(".")[-1].split("?")[0]}'
        
        # temporary fix because rn it only loads thumbnails
        # only for images idc about video
        # fuck you elon
        if glink.startswith("https://pbs.twimg.com/media/"):
            if glink.endswith(".jpg"):
                glink = glink.replace(".jpg", "?format=jpg&name=orig")
            elif glink.endswith(".png"):
                glink = glink.replace(".png", "?format=png&name=orig")
        
        download(glink, downloadpath, filename)

    # generate embed
    return anyembed(twlink, gallery[0], filename)


# twitter markdown for webhook
async def tw_markdown(link:str, webhook: DiscordWebhook):
    # get json from vxtwitter
    vxjson = vx_jsonget(link)
    
    # get gallery
    gallery = vxjson["mediaURLs"]
    
    # setup content
    content = f'[@{vxjson["user_screen_name"]} on Twitter](<{vxjson["tweetURL"]}>)'

    # add multiple posts if needed
    for glink in gallery:
        content += f' [{"-" if glink.split(".")[-1] == "png" else "~"}]({glink})'
    
    # modify content
    webhook.content = content