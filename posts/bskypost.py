import os
import re
from atproto import Client

from posts.post import Post, PostType

bsky = Client()
bsky.login('kapucni.bsky.social', os.getenv("BSKYPASS"))

class BskyPost(Post):
    _platform = "Bluesky"
    _prefix = "@"

    async def fetch(self):
        match = re.search(r'https://bsky\.app/profile/([^/]+)/post/([^/]+)', self._url)
        if not match:
            raise Exception("Invalid Bluesky link")

        self._author = match.group(1)
        self._id = match.group(2)

        user = bsky.get_profile(self._author)
        self._author_icon = user.avatar

        post = bsky.get_post(self._id, self._author)
        # TODO: surround links with <> to prevent embeds
        self._text = post.value.text


        if post.value.embed:
            if hasattr(post.value.embed, "images"):
                for media in post.value.embed.images:
                    self._media.append(f"https://cdn.bsky.app/img/feed_fullsize/plain/{user.did}/{media.image.ref.link}")
                self._type = PostType.IMAGE
            elif hasattr(post.value.embed, "video"):
                # TODO thumbnail
                self._media.append(f"https://bsky.social/xrpc/com.atproto.sync.getBlob?did={user.did}&cid={post.value.embed.video.ref.link}")
                self._type = PostType.VIDEO
            
            if len(self._media) > 1:
                self._type = PostType.GALLERY
                
        else:
            self._type = PostType.TEXT

        await super().fetch()
        