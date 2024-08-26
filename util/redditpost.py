import os
import re
import asyncpraw

from util.post import Post, PostType

reddit = asyncpraw.Reddit(
    client_id=os.getenv("REDDITCID"),
    client_secret=os.getenv("REDDITCSECRET"),
    user_agent="Lop_on_discord",
)

async def new_reddit_posts(subreddit: str, after, before):
    sub = await reddit.subreddit(subreddit)
    async for submission in sub.new(limit=10):
        if submission.created_utc > after and submission.created_utc < before:
            yield submission


class RedditPost(Post):
    _prefix = "u/"

    async def generate(self, submission):
        # url
        self._url = submission.shortlink

        # author
        author = await reddit.redditor(submission.author.name)
        await author.load()
        self._author = author.name
        self._author_icon = author.icon_img.split("?")[0]
        self._platform = (
            "Reddit"
            if submission.subreddit_type == "user"
            else submission.subreddit_name_prefixed
        )

        # TODO: id from shortlink

        # title
        self._title = submission.title

        # type
        self._type = RedditPost.post_type(submission)

        match self._type:
            case PostType.IMAGE:
                self._media.append(submission.url)

            case PostType.GALLERY:
                image_dict = submission.media_metadata
                for i in image_dict:
                    pattern = r"/([^/?]+)(?:\?|$)"
                    self._media.append(
                        "https://i.redd.it/"
                        + re.search(pattern, image_dict[i]["s"]["u"]).group(1)
                    )

            case PostType.VIDEO:
                # reddit is stupit and has the video and audio in separate sources
                # besides discord doesnt allow videos in embeds
                self._thumbnail = submission.thumbnail
                self._media.append(submission.media["reddit_video"]["fallback_url"])

            case PostType.POLL:
                # TODO
                self._text = "polls arent supported yet"

            case PostType.CROSSPOST:
                # TODO
                self._text = "crossposts arent supported yet"
                self._parent = Post(
                    reddit.submission(
                        url="https://reddit.com"
                        + submission.crosspost_parent_list[0]["permalink"]
                    )
                )
                # self._parent.fetch()

            case PostType.TEXT:
                self._text = submission.selftext

        await super().fetch()

    async def fetch(self):
        # fetch
        submission = await reddit.submission(url=self._url)
        await self.generate(submission)

    def post_type(subm) -> PostType:
        if getattr(subm, "post_hint", "") == "image":
            return PostType.IMAGE
        elif getattr(subm, "is_gallery", False):
            return PostType.GALLERY
        elif subm.is_video:
            return PostType.VIDEO
        elif hasattr(subm, "poll_data"):
            return PostType.POLL
        elif hasattr(subm, "crosspost_parent"):
            return PostType.CROSSPOST
        elif subm.is_self:
            return PostType.TEXT
        else:
            return PostType.UNKNOWN
