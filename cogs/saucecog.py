import discord
from discord import app_commands
from discord.ext import commands

import os
from pysaucenao import SauceNao

from util.loghelper import log_cog_load
from util.msgutil import *


class SauceCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.sauceapi = SauceNao(api_key=os.getenv("SAUCETOKEN"))
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="SauceNAO",
            callback=self.saucefind,
        )
        self.bot.tree.add_command(self.ctx_menu)
        log_cog_load(self)


    # reverse image search with saucenao
    async def saucefind(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)

        piclinks = getattachmenturls(message)

        if len(piclinks) > 0:
            try:
                results = await self.sauceapi.from_url(piclinks[0])
            except any:
                await errorfollowup(interaction, "Something went wrong")
                return

            if len(results) != 0:
                embed = discord.Embed(
                    title="Sauce found",
                    url=f"https://saucenao.com/search.php?db=999&url={piclinks[0]}",
                    color=0x5865F2,
                )
                embed.set_thumbnail(url=results[0].thumbnail)
                for r in results:
                    if r.index is not None and r.url is not None:
                        embed.add_field(
                            name=f"{r.index} | {r.similarity}%"
                            + (
                                f" | {r.author_name}"
                                if r.author_name is not None
                                else ""
                            ),
                            value=f"{r.url}",
                            inline=False,
                        )

                embed.set_footer(
                    text=f"limit {results.short_remaining}s {results.long_remaining}d"
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

            else:
                await errorfollowup(interaction, "Sauce not found")

        else:
            await errorfollowup(
                interaction, "The message must contain one and only one attachment"
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SauceCog(bot))
