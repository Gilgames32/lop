import discord
from discord import app_commands
from discord.ext import commands

from util.const import *
from util.loghelper import log_cog_load, log_command
from util.msgutil import *

class HoneyPotCog(commands.Cog):
    MESSAGE = """
# claim your free ban here
just send any message in this channel and get a free ban

ban enjoyers: {}
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        log_cog_load(self)

    
    # twitter markdown with extra steps
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
    @app_commands.command(name="honeypot", description="toggle honeypot in a channel")
    async def toggle(self, interaction: discord.Interaction):
        log_command(interaction)
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)

        ch_id = str(interaction.channel.id)
        try:
            if ch_id not in conf["honeypot"]:
                message = await interaction.channel.send(HoneyPotCog.MESSAGE.format(0))
                
                conf["honeypot"][ch_id] = {
                    "message": message.id,
                    "falls": 0
                }
                saveconf()
                await interaction.followup.send("Honeypot enabled", ephemeral=True)
            else:
                try:
                    counter = await interaction.channel.fetch_message(conf["honeypot"][ch_id]["message"])
                    await counter.delete()
                except Exception as e:
                    log.error(f"Failed to delete honeypot counter message in channel {interaction.channel.id}: {e}")
                del conf["honeypot"][ch_id]
                saveconf()
                await interaction.followup.send("Honeypot disabled", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)[:2000]))
        

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore bots
        if message.author.bot:
            return

        ch_id = str(message.channel.id)
        if ch_id in conf["honeypot"]:
            try:
                # ban
                await message.guild.ban(message.author, reason="fell in the honeypot")
                
                # update counter
                conf["honeypot"][ch_id]["falls"] += 1
                saveconf()
                falls = conf["honeypot"][ch_id]["falls"]
                counter = await message.channel.fetch_message(conf["honeypot"][ch_id]["message"])
                await counter.edit(content=HoneyPotCog.MESSAGE.format(falls))

                log.info(f"{message.author.mention} {message.author.name} fell in the honeypot in channel {message.channel.id}")
            except Exception as e:
                log.error(f"Failed to ban {message.author.mention} {message.author.name} in honeypot channel {message.channel.id}: {e}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HoneyPotCog(bot))
