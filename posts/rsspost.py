import requests
import os

from posts.post import Post, PostType


class RSSPost(Post):
    DEFAULT_AVATAR = "https://raw.githubusercontent.com/Gilgames32/lop/main/lop_pfp.png"
    
    def __init__(self, item, feed):
        super().__init__("")

        self._title = getattr(item, "title", "Untitled post")
        self._author = getattr(feed.feed, "title", "Unknown feed")
        self._url = getattr(item, "link", None)
        self._platform = getattr(feed.feed, "link", "https://RSS")[8:]
        
        self._fetched = True
        self._type = PostType.TEXT

    def get_avatar(self):
        return self.DEFAULT_AVATAR
