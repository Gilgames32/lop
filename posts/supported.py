import re
from posts.post import Post
from posts.twitterpost import Tweet
from posts.redditpost import RedditPost
from posts.pixivpost import PixivPost
from posts.esixpost import EsixPost
from posts.bskypost import BskyPost

def anypost(url: str) -> Post:
    if not url.startswith("https://"):
        return None
    
    url = url.split("?")[0]
    
    patterns = {
        "twitter.com": (r"https://[^/]+/[^/]+/status/\d+", Tweet),
        "x.com": (r"https://[^/]+/[^/]+/status/\d+", Tweet),
        "reddit.com": (r"https://www\.reddit\.com/[ur]/[^/]+/[a-z]+/[^/]+", RedditPost),
        "redd.it": (r"https://redd\.it/\w+", RedditPost),
        "pixiv.net": (r"https://www\.pixiv\.net/en/artworks/\d+", PixivPost),
        "e621.net": (r"https://e\d+\.net/posts/\d+", EsixPost),
        "e926.net": (r"https://e\d+\.net/posts/\d+", EsixPost),
        "bsky.app": (r"https://bsky\.app/profile/[^/]+/post/[^/]+", BskyPost),
    }

    for domain, (pattern, post_class) in patterns.items():
        if domain in url and re.search(pattern, url):
            return post_class(url)
    
    return None

