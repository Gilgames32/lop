import feedparser
import calendar
import requests

from posts.post import Post
from posts.rsspost import RSSPost
from util.loghelper import log

class Feed(): 
    HEADERS = {"User-Agent": "Lop"}
    
    def __init__(self, url: str):
        self.url = url
        self.entries = []
        self.feed = None

    def fetch_feed(self):
        response = requests.get(self.url, headers=self.HEADERS, timeout=10)
        if response.status_code != 200:
            log.error(f"Failed to fetch feed {self.url} - {response.status_code}")
            return
        else:
            self.feed = feedparser.parse(response.text)

    def fetch_new_entries(self, after: float, before: float):
        if not self.feed:
            self.fetch_feed()
        if not self.feed:
            return

        self.entries = filter(lambda entry: after < calendar.timegm(entry.published_parsed) <= before, self.feed.entries)
        self.entries = sorted(self.entries, key=lambda entry: calendar.timegm(entry.published_parsed))

        for entry in self.entries:
            log.info(f"New post at {entry.published} - {getattr(entry, 'link', None)}")

    def get_posts(self) -> list[Post]:
        return list(map(lambda entry: RSSPost(entry, self.feed), self.entries))
    
    def get_last_post_time(self) -> float:
        if not self.entries:
            return 0.0
        return calendar.timegm(self.entries[-1].published_parsed)
