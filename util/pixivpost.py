import requests
from discord_webhook import DiscordWebhook

from util.urlparser import anyembed, download
from util.const import downloadpath
from util.msgutil import errorembed

# base header so that we dont get 403
pixiv_baseheader = lambda x: {
    "referer": f"https://www.pixiv.net/member_illust.php?mode=medium&illust_id={x}"
}


# fetch info from id
class PixivssssPost():
    def __init__(self, postid: int):
        artwork = requests.get(f"https://www.pixiv.net/ajax/illust/{postid}").json()[
            "body"
        ]
        self.artist = artwork["userName"]
        self.id = postid
        self.imgurl = artwork["urls"]["original"]
        self.imgext = None if self.imgurl is None else artwork["urls"]["original"].split(".")[-1]
        self.filename = f"{self.artist}_{self.id}.{self.imgext}"



import re
import requests

from util.post import Post, PostType
from util.urlparser import cleanurl

class PixivPost(Post):
    _platform = "Pixiv"
    _prefix = ""

    async def fetch(self):
        self._url = cleanurl(self._url)

        self._id = int(re.search(r"\d+", self._url).group())
        
        artwork = requests.get(f"https://www.pixiv.net/ajax/illust/{self._id}").json()[
            "body"
        ]
        
        self._author = artwork["userName"]
        self._author_icon = ""
        self._fullres = artwork["urls"]["original"]

        self._title = artwork["illustTitle"]
        self._text = artwork["description"]

        phixiv = requests.get(f"https://www.phixiv.net/api/info?id={self._id}").json()
        self._media = phixiv["image_proxy_urls"]

        self._type = PostType.GALLERY if len(self._media) > 1 else PostType.IMAGE

        await super().fetch()
