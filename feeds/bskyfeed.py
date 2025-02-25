from feeds.feed import Feed
from posts.bskypost import BskyPost


class BskyFeed(Feed):
    def get_posts(self) -> list[BskyPost]:
        return list(map(lambda entry: BskyPost(entry.link), self.entries))
    
