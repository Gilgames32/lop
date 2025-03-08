import os
import re
from atproto import Client

from posts.post import Post, PostType

bsky = Client()
bsky.login("kapucni.bsky.social", os.getenv("BSKYPASS"))

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

        user = bsky.get_profile(self._author)
        self._author_icon = user.avatar

        post = bsky.get_post(self._id, self._author)
        self._text = post.value.text

        embed_media = post.value.embed.media if hasattr(post.value.embed, "media") else post.value.embed if post.value.embed else None

        if embed_media:
            if hasattr(embed_media, "images"):
                for media in embed_media.images:
                    ext = media.image.mime_type.split("/")[-1]
                    self._media.append(f"https://cdn.bsky.app/img/feed_fullsize/plain/{user.did}/{media.image.ref.link}?.{ext}")
                self._type = PostType.IMAGE
            elif hasattr(embed_media, "video"):
                # TODO thumbnail
                ext = embed_media.video.mime_type.split("/")[-1]
                self._media.append(f"https://bsky.social/xrpc/com.atproto.sync.getBlob?did={user.did}&cid={embed_media.video.ref.link}&.{ext}")
                self._type = PostType.VIDEO
            
            if len(self._media) > 1:
                self._type = PostType.GALLERY
                
        else:
            self._type = PostType.TEXT

        await super().fetch()
        