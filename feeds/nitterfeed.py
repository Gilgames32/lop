from feeds.feed import Feed
from posts.twitterpost import Tweet

import feedparser
import requests
from selenium import webdriver
import re

from util.loghelper import log

class NitterFeed(Feed):
    POST_PATTERN = r"https://nitter.poast.org/([^/]+)/status/(\d+)"
    cookies_cache = {}

    def cookiegen(url):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')

        with webdriver.Firefox(options=options) as driver:
            driver.get(url)
            cookies = driver.get_cookies()
            driver.quit()

        return {cookie['name']: cookie['value'] for cookie in cookies} # i love python

    def fetch_feed(self):
        response = requests.get('https://nitter.poast.org/kapucni_/rss', headers=Feed.HEADERS, cookies=NitterFeed.cookies_cache)
        
        if response.status_code != 200:
            # retry by refetching the cookies
            NitterFeed.cookies_cache = NitterFeed.cookiegen("https://nitter.poast.org/kapucni_/rss")
            log.info(f"New cookies: {NitterFeed.cookies_cache}")
            response = requests.get('https://nitter.poast.org/kapucni_/rss', headers=Feed.HEADERS, cookies=NitterFeed.cookies_cache)
            if response.status_code != 200:
                raise Exception("Failed to fetch feed")
        
        self.feed = feedparser.parse(response.text)

    def get_posts(self) -> list[Tweet]:
        # TODO: filter
        return list(map(NitterFeed.tweetify, self.entries))

    def tweetify(entry):
        match = re.search(NitterFeed.POST_PATTERN, entry.link)
        
        if not match:
            raise Exception("Invalid tweet link")

        return Tweet(f"https://twitter.com/{match.group(1)}/status/{match.group(2)}")
