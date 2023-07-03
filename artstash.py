from discord_webhook import DiscordWebhook
from urlparser import cleanurl
from stash_esix import esix_download, esix_markdown
from stash_twitter import tw_download, tw_markdown
from stash_pixiv import pixiv_download, pixiv_markdown

hosts = {
    "e621.net": {
        "download": esix_download,
        "markdown": esix_markdown,
    },
    "e926.net": {
        "download": esix_download,
        "markdown": esix_markdown
    },
    "twitter.com": {
        "download": tw_download,
        "markdown": tw_markdown
    },
    "fxtwitter.com": {
        "download": tw_download,
        "markdown": tw_markdown
    },
    "vxtwitter.com": {
        "download": tw_download,
        "markdown": tw_markdown
    },
    "www.pixiv.net": {
        "download": pixiv_download,
        "markdown": pixiv_markdown
    },
    
}

def anydownload(link: str):
    # strip url
    link = cleanurl(link)

    for host in hosts:
        if link.startswith(f"https://{host}/"):
            return hosts[host]["download"](link)
        

def anymkwebhook(link: str, webhook: DiscordWebhook):
    # strip url
    link = cleanurl(link)

    for host in hosts:
        if link.startswith(f"https://{host}/"):
            hosts[host]["markdown"](link, webhook)
            return True
    else:
        return False