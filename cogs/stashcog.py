import discord
from discord import app_commands
from discord.ext import commands
from discord_webhook import DiscordWebhook

from util.const import *
from util.msgutil import *
from util.artstash import anydownload, anymkwebhook
from util.urlparser import downloadpath, cleanurl
from stash.stash_vxtwitter import vx_jsonget, tw_markdown


class StashCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Stash",
            callback=self.ctxdown,
        )
        self.bot.tree.add_command(self.ctx_menu, guild=labowor)
        print("Loaded", __class__.__name__)

    async def ctxdown(self, interaction: discord.Interaction, message: discord.Message):
        if not await devcheck(interaction):
            return
        embed = await anydownload(message.content)
        if embed is None:
            embed = errorembed(
                "The message must start with a valid link\n"
                "Currently supported sites: twitter, e621, e926, pixiv, reddit"
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # bulk download downloadables from channel history
    @app_commands.command(name="stash", description="bulk download old messages")
    @app_commands.describe(count="amount of messages processed")
    async def download_history(self, interaction: discord.Interaction, count: int):
        if not await devcheck(interaction):
            return

        await interaction.response.defer(ephemeral=True)

        dlcount = 0
        async for message in interaction.channel.history(limit=count):
            if message.author.bot:
                continue
            embed = await anydownload(message.content)
            if embed is not None:
                dlcount += 1
                await message.add_reaction("🔽")

        embed = discord.Embed(title=f"Downloaded {dlcount} posts", color=0x009AFE)
        embed.set_footer(text=downloadpath)
        await interaction.followup.send(embed=embed)

    # save any file to stash
    @app_commands.command(name="save", description="save any file to stash")
    async def save_file(
        self, interaction: discord.Interaction, file: discord.Attachment, filename: str
    ):
        if not await devcheck(interaction):
            return

        await interaction.response.defer()

        ext = file.filename.split(".")[-1]
        filename += "." + ext

        await file.save(downloadpath + filename)

        embed = discord.Embed(title=f"File saved", color=0x009AFE)
        embed.add_field(
            name=filename,
            value=f"{round(os.path.getsize(downloadpath + filename)/1024, 1)} KB",
        )
        embed.set_image(url=file.url)
        embed.set_footer(text=downloadpath)
        
        await interaction.followup.send(embed=embed, delete_after=(30 * 60))

    
    # twitter markdown with extra steps
    @app_commands.command(name="twitter", description="send twitter as markdown")
    async def save_file(
        self, interaction: discord.Interaction, link: str, impersonate: bool = True
    ):
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)

        vxjson = vx_jsonget(cleanurl(link))
        if vxjson is None:
            await interaction.followup.send(embed=errorembed("Invalid link"), ephemeral=True)
            return


        webhook = DiscordWebhook(
            url=webhookurl,
            content="",
            avatar_url=interaction.user.display_avatar.url if not impersonate else vxjson["user_profile_image_url"].replace("_normal", ""),
            username=interaction.user.display_name if not impersonate else vxjson["user_screen_name"],
        )


        if impersonate:
            webhook.content = f'[Brought to you by {interaction.user.display_name}](<{vxjson["tweetURL"]}>)'
        else:
            handle = "\@" + vxjson["user_screen_name"].replace("_", "\_")
            webhook.content = f'{handle} on [Twitter](<{vxjson["tweetURL"]}>)'

        for glink in vxjson["mediaURLs"]:
            webhook.content += f' [{"-" if glink.split(".")[-1] == "png" else "~"}]({glink})'

        # remove the last word (duplicate link)
        webhook.content += "\n" + " ".join(vxjson["text"].split(" ")[:-1])


        if interaction.channel.type == discord.ChannelType.public_thread:
            webhook.thread_id = interaction.channel.id
        
        webhook.execute()
        await interaction.followup.send("✅", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore bots
        if message.author.bot:
            return

        # auto download from #to-stash
        if message.channel.id == tostash_chid:
            embed = await anydownload(message.content)
            if embed is not None:
                await message.delete()
                await message.channel.send(embed=embed, delete_after=(30 * 60))

        # turn twitter and e6 links to better markdowns using webhooks
        # now with thread support
        elif (
            message.channel.id == tomarkdown_chid
            or message.channel.type == discord.ChannelType.public_thread
            and message.channel.parent_id == tomarkdown_chid
        ):
            firstlink = message.content.split(" ")[0]

            webhook = DiscordWebhook(
                url=webhookurl,
                content="",
                avatar_url=message.author.display_avatar.url,
                username=message.author.display_name,
            )

            if message.channel.type == discord.ChannelType.public_thread:
                webhook.thread_id = message.channel.id

            if await anymkwebhook(firstlink, webhook):
                webhook.execute()
                await message.delete()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StashCog(bot), guild=labowor)
