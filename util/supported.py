from util.post import Post, PostType
from util.twitterpost import Tweet
from util.redditpost import RedditPost
from util.pixivpost import PixivPost

def anypost(url: str) -> Post:
    if "twitter.com" in url:
        return Tweet(url)
    elif "x.com" in url:
        return Tweet(url)
    elif "reddit.com" in url:
        return RedditPost(url)
    elif "pixiv.net" in url:
        return PixivPost(url)
    else:
        print("Unsupported post type")
        return None

