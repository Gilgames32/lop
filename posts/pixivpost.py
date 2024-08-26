import requests
import re

from discord import Embed

from posts.post import Post, PostType

# base header so that we dont get 403
pixiv_baseheader = lambda x: {
    "referer": f"https://www.pixiv.net/member_illust.php?mode=medium&illust_id={x}"
}

class PixivPost(Post):
    _platform = "Pixiv"
    _prefix = ""

    async def fetch(self):
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

    def download(self, path: str) -> Embed:
        # skull emoji (im lazy)
        tmp = self._media
        self._media = [self._fullres]
        embed = super().download(path)
        self._media = tmp
        return embed
