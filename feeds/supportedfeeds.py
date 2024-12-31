import re

from feeds.feed import Feed
from feeds.bskyfeed import BskyFeed
from feeds.redditfeed import RedditFeed
from feeds.nitterfeed import NitterFeed


def anyfeed(url: str) -> Feed:
    if not url.startswith("https://"):
        return None
    
    url = url.split("?")[0]
    
    patterns = {
        "bsky": (r"https://bsky\.app/profile/[^/]+/rss", BskyFeed),
        "reddit": (r"https://www\.reddit\.com/[ru]/[^/]+/\.rss", RedditFeed),
        "nitter": (r"https://nitter\.poast\.org/[^/]+/rss", NitterFeed),
    }

    for domain, (pattern, feed_class) in patterns.items():
        if domain in url and re.search(pattern, url):
            return feed_class(url)
    
    return None

