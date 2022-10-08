from discord import *
from discord.ext import commands

client = commands.Bot(command_prefix=',')
token = "token"
gil = 465376961284276236


@client.event
async def on_ready():
    print(f'{client.user} reports for a minuscule amount of trolling')
    print(f'{round(client.latency*100)}ms')
    await client.change_presence(activity=Activity(type=ActivityType.watching, name="Gilgames's nightmares"))


@client.command()
async def ping(ctx):
    print(f'{ctx.message.author} called {ctx.message.content}')
    await ctx.send(f'{round(client.latency * 100)}ms')


@client.command(name='clear', help='this command will clear msgs')
async def clear(ctx, amount=2):
    print(f'{ctx.message.author} called {ctx.message.content}')
    if ctx.message.author.id != gil:
        await ctx.send(f"Only Gilgames can use this command")
        return

    await ctx.channel.purge(limit=amount)


@client.command()
async def say(ctx, *, text):
    print(f'{ctx.message.author} called {ctx.message.content}')
    if ctx.message.author.id != gil:
        await ctx.send(f"Only Gilgames can use this command")
        return

    await ctx.message.delete()
    await ctx.send(text)


@client.command()
async def backup(ctx, type, discord_id):
    print(f'{ctx.message.author} called {ctx.message.content}')
    if ctx.message.author.id != gil:
        await ctx.send(f"Only Gilgames can use this command")
        return

    if type in ('all', 'everything', '*'):
        source_channel = client.get_channel(int(discord_id))
        async for msg in source_channel.history(limit=1000, oldest_first=True):
            await ctx.send(f'{msg.author}\n{msg.content}')
            if msg.attachments:
                for att in msg.attachments:
                    await ctx.send(f'{att.url}')

    elif type in ('media', 'images'):
        source_channel = client.get_channel(int(discord_id))
        async for msg in source_channel.history(limit=1000, oldest_first=True):
            if msg.embeds:
                for emb in msg.embeds:
                    await ctx.send(f'{msg.author}\n{emb.url}')
            if msg.attachments:
                for att in msg.attachments:
                    await ctx.send(f'{msg.author}\n{att.url}')

    elif type in ('emote', 'emotes', 'emoji', 'emojis'):
        server = client.get_guild(int(discord_id))
        for emo in server.emojis:
            await ctx.send(f'{emo.name}\n{emo.url_as()}')

    elif type in ('pin', 'pinned', 'pins'):
        server = client.get_guild(int(discord_id))
        for tc in server.text_channels:
            pins = await tc.pins()
            if len(pins) != 0:
                await ctx.send(f'**{tc.name}**')
                for pin in pins:
                    await ctx.send(f'{pin.author}\n{pin.content}')
                    if pin.attachments:
                        for att in pin.attachments:
                            await ctx.send(f'{att.url}')

    elif type in ('ban', 'bans', 'banned', 'banneds'):
        server = client.get_guild(int(discord_id))
        bans = await server.bans()
        for ban in bans:
            await ctx.send(f'`{ban.user.id}`: {ban.user.name} ')


client.run(token)
