import re
import requests

from util.post import Post, PostType
from util.urlparser import cleanurl

class Tweet(Post):
    _platform = "Twitter"
    _prefix = "@"

    async def fetch(self):
        # remove trackers
        self._url = cleanurl(self._url)

        photo = False
        
        photopattern = r"https://[^/]+/([^/]+)/status/(\d+)/photo/(\d+)"
        match = re.search(photopattern, self._url)
        if match:
            photo = int(match.group(3))
            pass
        else:
            pattern = r"https://[^/]+/([^/]+)/status/(\d+)"
            match = re.search(pattern, self._url)
            if not match:
                raise Exception("Invalid tweet link")
        
        self._author = match.group(1)
        self._id = match.group(2)

        self._url = f"https://twitter.com/{self._author}/status/{self._id}"

        if photo:
            self._url += f"/photo/{photo}"

        
        # get json from vxtwitter
        vxjson = requests.get(f"https://api.vxtwitter.com/{self._author}/status/{self._id}").json()
        
        # media
        if photo:
            self._media.append(vxjson["mediaURLs"][photo - 1])
        else:
            for media in vxjson["mediaURLs"]:
                # i hate compression so much dude its unreal
                if media.endswith(".jpg"):
                    media = media.replace(".jpg", "?format=jpg&name=orig")
                elif media.endswith(".png"):
                    media = media.replace(".png", "?format=png&name=orig")
                self._media.append(media)
        
        # pfp
        self._author_icon = vxjson["user_profile_image_url"]

        # text
        self._text = vxjson["text"]
        split = self._text.split(" ")
        if split[-1].startswith("https://t.co/"):
            self._text = " ".join(split[:-1])

        # type
        if not self._media:
            self._type = PostType.TEXT
        elif len(self._media) > 1:
            self._type = PostType.GALLERY
        elif self._media[0].endswith("mp4"):
            self._thumbnail = vxjson["media_extended"][0]["thumbnail_url"]
            self._type = PostType.VIDEO
        elif self._media[0].endswith("jpg") or self._media[0].endswith("png"):
            self._type = PostType.IMAGE
        else:
            self._type = PostType.UNKNOWN

        await super().fetch()
