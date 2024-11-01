import re
from posts.post import Post
from posts.twitterpost import Tweet
from posts.redditpost import RedditPost
from posts.pixivpost import PixivPost
from posts.esixpost import EsixPost

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
        pattern = r"https://www\.reddit\.com/[a-z]/[^/]+/comments/[^/]+/[^/]+"
        if re.search(pattern, url):
            return RedditPost(url)
    elif "redd.it" in url:
        pattern = r"https://redd\.it/\w+"
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

