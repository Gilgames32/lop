from discord_webhook import DiscordWebhook
import e621
import os

from util.post import Post, PostType

esix = e621.E621(("kapucni", os.getenv("E621TOKEN")))

class EsixPost(Post):
    _platform = "E621"
    _prefix = ""

    async def fetch(self):
        self._id = int(self._url.split("/")[4])
        epost = esix.posts.get(self._id)
        # remove conditional dnp from artists
        if "conditional_dnp" in epost.tags.artist:
            epost.tags.artist.remove("conditional_dnp")

        # if it really has no artist
        if epost.tags.artist == []:
            epost.tags.artist.append("unknown")


        self._author = epost.tags.artist[0]
        self._author_icon = ""
        self._media = [epost.file.url]

        self._type = PostType.IMAGE if epost.file.ext in ["png", "jpg", "jpeg", "gif"] else PostType.VIDEO

        await super().fetch()
