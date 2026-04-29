from feeds.feed import Feed
from posts.redditpost import RedditPost

import feedparser
import requests

class RedditFeed(Feed):
    def get_posts(self) -> list[RedditPost]:
        return list(map(lambda entry: RedditPost(entry.link), self.entries))