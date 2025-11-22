import re
import requests

from posts.post import Post, PostType

BSKY_ENDPOINT = "https://public.api.bsky.app/xrpc/"

class BskyPost(Post):
    _platform = "Bluesky"
    _prefix = ""

    async def fetch(self):
        if self._fetched:
            return
        
        match = re.search(r"https://bsky\.app/profile/([^/]+)/post/([^/]+)", self._url)
        if not match:
            raise Exception("Invalid Bluesky link")

        self._author = match.group(1)
        self._id = match.group(2)

        re_user = requests.get(BSKY_ENDPOINT + "app.bsky.actor.getProfile", params={
            "actor": self._author
        })
        if re_user.status_code != 200:
            raise Exception("Failed to fetch Bluesky user profile")
        user_data = re_user.json()
        self._author = user_data["handle"]
        self._author_icon = user_data["avatar"]
        udid = user_data["did"]

        re_post = requests.get(BSKY_ENDPOINT + "app.bsky.feed.getPostThread", params={
            "uri": f"at://{udid}/app.bsky.feed.post/{self._id}",
            "depth": 0,
            "parentHeight": 0
        })
        if re_post.status_code != 200:
            raise Exception("Failed to fetch Bluesky post")
        post_data = re_post.json()
        record_data = post_data["thread"]["post"]["record"]

        self._text = record_data.get("text", "")
        self._type = PostType.TEXT

        embed_data = record_data.get("embed", None)
        if embed_data:
            # video
            if embed_data.get("video", None):
                embed_media = embed_data["video"]
                ext = embed_media["mimeType"].split("/")[-1]
                self._media.append(f"https://bsky.social/xrpc/com.atproto.sync.getBlob?did={udid}&cid={embed_media['ref']['$link']}&.{ext}")
                self._thumbnail = post_data["thread"]["post"]["embed"]["thumbnail"]
                self._type = PostType.VIDEO
            
            else:
                # gallery
                if embed_data.get("media", None):
                    embed_media = embed_data["media"]["images"]
                # image
                elif embed_data.get("images", None):
                    embed_media = embed_data["images"]

                for image in embed_media:
                    image = image["image"]
                    ext = image["mimeType"].split("/")[-1]
                    if ext == "jpeg":
                        ext = "png" # its that easy :3c 
                    self._media.append(f"https://cdn.bsky.app/img/feed_fullsize/plain/{udid}/{image['ref']['$link']}?.{ext}")
                
                self._type = PostType.GALLERY if len(self._media) > 1 else PostType.IMAGE

        await super().fetch()
        