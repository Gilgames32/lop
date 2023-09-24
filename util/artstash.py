from discord_webhook import DiscordWebhook
from util.urlparser import cleanurl
from stash.stash_esix import esix_download, esix_markdown
from stash.stash_vxtwitter import tw_download, tw_markdown
from stash.stash_pixiv import pixiv_download, pixiv_markdown
from stash.stash_reddit import reddit_download, reddit_markdown

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
    "x.com": {
        "download": tw_download,
        "markdown": tw_markdown
    },
    "www.reddit.com": {
        "download": reddit_download,
        "markdown": reddit_markdown
    }
}

async def anydownload(link: str):
    # strip url
    link = cleanurl(link)

    for host in hosts:
        if link.startswith(f"https://{host}/"):
            return await hosts[host]["download"](link)
        

async def anymkwebhook(link: str, webhook: DiscordWebhook):
    # strip url
    link = cleanurl(link)

    for host in hosts:
        if link.startswith(f"https://{host}/"):
            await hosts[host]["markdown"](link, webhook)
            return True
    else:
        return False