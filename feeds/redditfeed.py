from feeds.feed import Feed
from posts.redditpost import RedditPost

import feedparser
import requests

class RedditFeed(Feed):
    def fetch_feed(self):
        response = requests.get(self.url, headers=Feed.HEADERS)
        self.feed = feedparser.parse(response.text)

    def get_posts(self) -> list[RedditPost]:
        return list(map(lambda entry: RedditPost(entry.link), self.entries))