import requests
import os
import asyncpraw
import time

from discord_webhook import DiscordWebhook
from dotenv import load_dotenv

from util.urlparser import anyembed, download, downloadpath, cleanurl
from util.const import loadjson, savejson


# init
load_dotenv()
client_id = os.getenv("REDDITCID")
client_secret = os.getenv("REDDITCSECRET")
app_name = 'Lop_on_discord'

class LopReddit():
    def __init__(self) -> None:
        self.api = self.reddit_auth()

    def reddit_auth(self):
        # use the reddit api to authenticate the client and obtain an access token
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        headers = {'User-Agent': app_name}
        data = {'grant_type': 'client_credentials'}
        response = requests.post('https://www.reddit.com/api/v1/access_token', auth=auth, data=data, headers=headers)
        access_token = response.json()['access_token']

        # use the access token to authenticate the client
        return asyncpraw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=app_name, access_token=access_token)

    # check if we need to request a new token (has to be done after restart and every hour)
    def reddit_reauth(self):
        conf = loadjson("conf")
        if conf["reddit_token_birth"] + 360 < time.time() or self.api is None:
            self.api = self.reddit_auth()
            conf["reddit_token_birth"] = time.time()
            savejson("conf", conf)


# fetch info from id
class RedditPost:
    def __init__(self, link: str):
        # pyhtons ternary operator is retarded
        self.id = link.split("/")[6] if link.startswith("https://") else link
    
    async def fetch(self):
        post = await reddit.api.submission(self.id)
        
        self.medialink = post.url
        if post.is_video:
            # it doesnt have sound but i dont need it anyway
            self.medialink = cleanurl(post.media['reddit_video']['fallback_url'])
        
        self.ext = self.medialink.split(".")[-1]
        self.author = post.author.name


reddit = LopReddit()


# downloads a reddit link
async def reddit_download(link: str):
    # refresh token
    reddit.reddit_reauth()
    
    # get post
    post = RedditPost(link)
    await post.fetch()
    
    # download in artist_postid.ext format
    filename = f"{post.author}_{post.id}.{post.ext}"
    download(post.medialink, downloadpath, filename)

    # generate embed
    return anyembed(link, post.medialink, filename)


# reddit markdown for webhook
async def reddit_markdown(link:str, webhook: DiscordWebhook):
    # refresh token
    reddit.reddit_reauth()

    # get post
    post = RedditPost(link)
    await post.fetch()
    
    # modify content
    webhook.content = f'[u/{post.author} on reddit](<{link}>)' \
                    + f' [{"-" if post.ext == "png" else "~"}]({post.medialink})'
    