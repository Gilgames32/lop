from feeds.feed import Feed
from posts.redditpost import RedditPost

import feedparser
import requests

class RedditFeed(Feed):
    def fetch_feed(self):
        response = requests.get('https://www.reddit.com/r/Szormok_AVE/.rss', headers=Feed.HEADERS)
        self.feed = feedparser.parse(response.text)

    def get_posts(self):
        return map(lambda entry: RedditPost(entry.link), self.entries)