import re
from util.post import Post, PostType
from util.twitterpost import Tweet
from util.redditpost import RedditPost
from util.pixivpost import PixivPost
from util.esixpost import EsixPost

def anypost(url: str) -> Post:
    if not url.startswith("https://"):
        return None
    
    url = url.split("?")[0]
    
    # FIXME: repeated code
    if "twitter.com" in url or "x.com" in url:
        pattern = r"https://[^/]+/[^/]+/status/\d+"
        if re.search(pattern, url):
            return Tweet(url)
        
    elif "reddit.com" in url:
        # TODO: reddit short urls?
        pattern = r"https://www\.reddit\.com/[a-z]/[^/]+/comments/[^/]+/[^/]+"
        if re.search(pattern, url):
            return RedditPost(url)
        
    elif "pixiv.net" in url:
        pattern = r"https://www\.pixiv\.net/en/artworks/\d+"
        if re.search(pattern, url):
            return PixivPost(url)
    
    elif "e621.net" in url or "e926.net" in url:
        pattern = r"https://e\d+\.net/posts/\d+"
        if re.search(pattern, url):
            return EsixPost(url)
    
    return None

