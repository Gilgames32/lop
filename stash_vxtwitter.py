import requests
from discord_webhook import DiscordWebhook
from urlparser import anyembed

from urlparser import download, downloadpath, cleanurl

# temporary fix because fuck you elon
# returns a json with the info of the given tweet
def vx_jsonget(twlink: str):
    # clean trackers
    twlink = cleanurl(twlink)

    # replace with d.fxtwitter
    hosts = ["twitter", "fxtwitter", "vxtwitter"]
    for h in hosts:
        if twlink.startswith(f"https://{h}.com/"):
            twlink = twlink.replace(h, "api.vxtwitter")
    # TODO: photos/1 and shi
    return requests.get(twlink).json()


# dowload from twitter
def tw_download(twlink: str):
    # get json from vxtwitter
    vxjson = vx_jsonget(twlink)

    # get gallery
    gallery = vxjson["mediaURLs"]
    for i, glink in enumerate(gallery):
        # download in artist_postid_gidx.ext format
        filename = f'{vxjson["user_screen_name"]}_{vxjson["tweetID"]}{"_"+str(i) if len(gallery) > 1 else ""}.{glink.split(".")[-1]}'
        download(glink, downloadpath, filename)

    # generate embed
    return anyembed(twlink, gallery[0], filename)


# twitter markdown for webhook
def tw_markdown(link:str, webhook: DiscordWebhook):
    # get json from vxtwitter
    vxjson = vx_jsonget(link)
    
    # get gallery
    gallery = vxjson["mediaURLs"]
    
    # setup content
    content = f'[{vxjson["user_screen_name"]} on Twitter](<{vxjson["tweetURL"]}>)'

    # add multiple posts if needed
    for glink in gallery:
        content += f' [{"-" if glink.split(".")[-1] == "png" else "~"}]({glink})'
    
    # modify content
    webhook.content = content