import discord
from discord import app_commands
from discord.ext import commands
from discord_webhook import DiscordWebhook

import feedparser
import time
import requests
import asyncio

from util.const import *
from util.msgutil import *


async def nitter_loop():
    while True:
        # 4 hours
        await asyncio.sleep(4 * 3600)
        await nitter_parse_followed()


def nitter_parse_user(user: str):
    # load feed
    feed = feedparser.parse(f"https://nitter.poast.org/{user}/rss")

    for post in feed["entries"]:
        author: str = post["author"]
        title: str = post["title"]
        timestamp = time.mktime(post["published_parsed"])

        # skip already processed
        if timestamp < conf["last_rss"]:
            # assuming they are in chronological order we can break once we encounter a skippable one
            break

        # skip retweets, replies
        if (
            author != f"@{user}"
            or title.startswith(f"RT by ")
            or title.startswith("R to ")
        ):
            continue

        id: str = post["link"][-21:-2]
        apivxlink: str = f"https://api.vxtwitter.com/status/{id}"
        vxjson = requests.get(apivxlink).json()
        gallery = vxjson["mediaURLs"]

        # skip posts without images
        if len(gallery) < 1:
            continue

        # make webhook
        webhook = DiscordWebhook(
            url=webhookurl,
            content="",
            avatar_url=str(vxjson["user_profile_image_url"]).replace("_normal", ""),
            username=user,
        )
        content = title + f'\n[original](<{vxjson["tweetURL"]}>)'
        for glink in gallery:
            content += f' [{"-" if glink.split(".")[-1] == "png" else "~"}]({glink})'
        webhook.content = content

        webhook.execute()


async def nitter_parse_followed():
    # parese users
    for user in conf["twfollows"]:
        nitter_parse_user(user)

    # record last sync time
    conf["last_rss"] = time.time()
    savejson("conf", conf)


class NitterFeedCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        asyncio.get_event_loop().create_task(nitter_loop())
        print("Loaded", __class__.__name__)

    # add follows
    @app_commands.command(
        name="follow", description="follow a twitter user for rss"
    )
    @app_commands.describe(user="The tag of the user to follow")
    async def nitter_follow(self, interaction: discord.Interaction, user: str):
        if not await devcheck(interaction):
            return
        if user not in conf["twfollows"]:
            conf["twfollows"].append(user)
            savejson("conf", conf)
        await interaction.response.send_message(f"Followed user {user}", ephemeral=True)

    # remove follows
    @app_commands.command(
        name="unfollow", description="unollows a twitter user for rss"
    )
    @app_commands.describe(user="The tag of the user to unfollow")
    async def nitter_unfollow(self, interaction: discord.Interaction, user: str):
        if not await devcheck(interaction):
            return
        if user in conf["twfollows"]:
            conf["twfollows"].remove(user)
            savejson("conf", conf)
        await interaction.response.send_message(
            f"Unfollowed user {user}", ephemeral=True
        )

    # manual sync
    @app_commands.command(name="nsync", description="force parse rss follows")
    async def nsync(self, interaction: discord.Interaction):
        if not await devcheck(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        await nitter_parse_followed()
        await interaction.followup.send("Done")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NitterFeedCog(bot), guild=labowor)
