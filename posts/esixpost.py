import requests
import os

from posts.post import Post, PostType


class EsixPost(Post):
    _platform = "E621"
    _prefix = ""

    _endpoint = "https://e621.net/posts.json?tags=id:"
    _user_agent = "Lop on Discord by Kapucni"

    async def fetch(self):
        if self._fetched:
            return
        
        self._id = self._url.split("/")[4]

        response = requests.get(self._endpoint + self._id, headers={"User-Agent": self._user_agent})
        if response.status_code != 200:
            raise Exception("Error fetching post from E621")

        posts = response.json()["posts"]
        if not posts:
            raise Exception("Post not found")
        post = posts[0]

        artists = post["tags"]["artist"]
        if "conditional_dnp" in artists: artists.remove("conditional_dnp")
        self._author = artists[0] if artists else "unknown"

        self._author_icon = ""

        self._media.append(post["file"]["url"])

        self._type = (
            PostType.IMAGE
            if post["file"]["ext"] in ["png", "jpg", "jpeg", "gif"]
            else PostType.VIDEO
        )

        await super().fetch()
