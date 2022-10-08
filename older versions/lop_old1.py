from discord import *
from discord.ext import commands
import json
import datetime
import random
import os

# initialization
fnj = "lop_data.json"
intents = Intents.all()
client = commands.Bot(command_prefix=',', intents=intents)

with open("token.txt", "r") as tokenfile:
    for line in tokenfile:
        token = line
        break

gil = 954419840251199579
# gil = 465376961284276236
imo = 890963749115150357
with open(fnj, "r") as read_file:
    data = json.load(read_file)


# function to save the data
def save_data():
    with open(fnj, "w+") as fp:
        json.dump(data, fp, sort_keys=True, indent=4)


async def checkwhitelist(ctx):
    serverid = str(ctx.message.guild.id)
    if serverid not in data["whitelist"]:
        data["whitelist"][serverid] = {str(gil): "Gilgames"}
        save_data()
    if str(ctx.message.author.id) not in data["whitelist"][serverid]:
        await ctx.send(f"Only whitelisted users can use this command")
        return True


"""for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")"""


# when the client is ready
@client.event
async def on_ready():
    print(f"{client.user} reports for a minuscule amount of trolling")
    print(f"{round(client.latency * 100)}ms")
    await client.change_presence(activity=Activity(type=ActivityType.watching, name="Gilgames's nightmares"))


# COMMANDS


# whitelist management, todo better json
@client.command(aliases=["wl", "wlist"], help="Manages whitelisted user")
async def whitelist(ctx, command="l", iid=0):
    # check GIL
    if ctx.message.author.id not in (gil, imo):
        await ctx.send(f"Only Gilgames can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")

    serverid = str(ctx.message.guild.id)
    if serverid not in data["whitelist"]:
        data["whitelist"][serverid] = {"465376961284276236": "Gilgames"}
        save_data()
    # list whitelisted users
    if command in ("list", "l"):
        await ctx.send(f'```json\n{json.dumps(data["whitelist"][serverid], indent=4, sort_keys=True)}```')

    else:
        try:
            iid = int(iid)
            wuser = await client.fetch_user(iid)
            if wuser is None:
                await ctx.send(f"Invalid user ID")
                return
        except:
            await ctx.send(f"Invalid user ID (ID must be an integer)")
            return

        # add user to whitelist
        if command in ("add", "promote"):
            data["whitelist"][serverid][str(iid)] = wuser.name
            save_data()
            await ctx.send(f"{wuser.name} has been added to the whitelist")

        # remove user from whitelist
        elif command in ("remove", "demote", "rm"):
            data["whitelist"][serverid].pop(str(iid), None)
            save_data()
            await ctx.send(f"{wuser.name} has been removed from the whitelist")

        else:
            await ctx.send(f"Invalid command")


# latency
@client.command(help="Returns the client's latency")
async def ping(ctx):
    if str(ctx.message.author.id) not in data["whitelist"][str(ctx.message.guild.id)]:
        await ctx.send(f"Only whitelisted users can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")
    await ctx.send(f"{round(client.latency * 100)}ms")


# bulk delete any amount of messages
@client.command(aliases=["purge", "cls"], help="Deletes a certain amount of messages")
async def clear(ctx, amount=2):
    if ctx.message.author.id not in (gil, imo):
        await ctx.send(f"Only Gilgames can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")
    if ctx.message.author.id not in (gil, imo):
        await ctx.send(f"Only Gilgames can use this command")
        return

    await ctx.channel.purge(limit=amount)


# make the bot say something
@client.command(help="Makes the bot say something")
async def say(ctx, *, text):
    if ctx.message.author.id not in (gil, imo):
        await ctx.send(f"Only Gilgames can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")
    await ctx.message.delete()
    await ctx.send(text)


@client.command(aliases=["b", "copy"], help="Makes a backup of the last given amount of messages in the current channel"
                                            "\n"
                                            "Commands: all, media, emotes, pins, bans, embeds\n"
                                            "When only_new is 1 (default) it will only backup stuff since the last one")
async def backup(ctx, command, discord_id, amount=512, only_new=1):
    if ctx.message.author.id not in (gil, imo):
        await ctx.send(f"Only Gilgames can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")

    # check if id is valid
    try:
        discord_id = int(discord_id)
    except:
        await ctx.send(f"Invalid ID (ID must be an integer)")
        return

    if discord_id == 0:
        channel_id = ctx.channel.id

    elif client.get_channel(discord_id) is not None:
        # id was channel id
        source_channel = client.get_channel(discord_id)
        channel_id = str(discord_id)
        source_server = client.get_channel(int(channel_id)).guild
        server_id = str(source_server.id)
    elif client.get_guild(discord_id) is not None:
        # id was server id
        source_channel = None
        channel_id = ""
        source_server = client.get_guild(discord_id)
        server_id = str(discord_id)

    else:
        await ctx.send(f"Invalid ID")
        return

    # server wide

    if server_id not in data["bdate"]:
        data["bdate"][server_id] = {}

    # emotes
    if command in ("emote", "emotes", "emoji", "emojis"):
        if "emotes" not in data["bdate"][server_id]:
            data["bdate"][server_id]["emotes"] = 0
        for emo in source_server.emojis:
            if emo.created_at.timestamp() > data["bdate"][server_id]["emotes"] or only_new != 1:
                await ctx.send(f"`{emo.name}`\n{emo.url_as()}")
        data["bdate"][server_id]["emotes"] = datetime.datetime.now().timestamp()

    # bans
    elif command in ("ban", "bans", "banned", "banneds"):
        bans = await source_server.bans()
        tosend = f"Users banned from `{server_id}`:"
        for ban in bans:
            tosend += f"\n`{ban.user.id}` - {ban.user.name} "
        await ctx.send(tosend)

    # pins
    elif command in ("pin", "pinned", "pins"):
        if "pins" not in data["bdate"][server_id]:
            data["bdate"][server_id]["pins"] = 0
            save_data()
        for tc in source_server.text_channels:
            pins = await tc.pins()
            if len(pins) != 0:
                tosend = ""
                for pin in pins:
                    if pin.created_at.timestamp() > data["bdate"][server_id]["pins"] or only_new != 1:
                        tosend += f"\n\n{pin.author}\n{pin.content}"
                        if pin.attachments:
                            for att in pin.attachments:
                                tosend += f"{att.url}"
                if tosend != "":
                    await ctx.send(f"`{tc.name}`{tosend}")
        data["bdate"][server_id]["pins"] = datetime.datetime.now().timestamp()

    else:
        # channel wide
        if channel_id not in data["bdate"][server_id]:
            data["bdate"][server_id][channel_id] = 0
            save_data()

        # everything
        if command in ("all", "everything", "*"):
            async for msg in source_channel.history(limit=amount, oldest_first=True):
                if msg.created_at.timestamp() > data["bdate"][server_id][channel_id] or only_new != 1:  # this
                    tosend = f"{msg.author}\n{msg.content}"
                    if msg.attachments:
                        for att in msg.attachments:
                            tosend += f"\n{att.url}"
                    await ctx.send(tosend)
            data["bdate"][server_id][channel_id] = datetime.datetime.now().timestamp()

        # link embeds and images
        elif command in ("media", "images"):
            async for msg in source_channel.history(limit=amount, oldest_first=True):
                if msg.created_at.timestamp() > data["bdate"][server_id][channel_id] or only_new != 1:
                    tosend = ""
                    if msg.embeds:
                        for emb in msg.embeds:
                            tosend += f"\n{emb.url}"
                    if msg.attachments:
                        for att in msg.attachments:
                            tosend += f"\n{att.url}"
                    if tosend != "":
                        await ctx.send(f"{msg.author}: {tosend}")
            data["bdate"][server_id][channel_id] = datetime.datetime.now().timestamp()

        # embeds (non-link embeds)
        elif command in ("embed", "embeds"):
            async for msg in source_channel.history(limit=amount, oldest_first=True):
                if msg.created_at.timestamp() > data["bdate"][server_id][channel_id] or only_new != 1:
                    if msg.embeds:
                        for emb in msg.embeds:
                            await ctx.send(embed=emb.copy())
            data["bdate"][server_id][channel_id] = datetime.datetime.now().timestamp()

        else:
            await ctx.send(f"Invalid argument")

    save_data()


@client.command(aliases=["touchgrass", "shower"], help="Warns members playing forbidden games")
async def grass(ctx):
    if ctx.message.author.id not in (gil, imo):
        await ctx.send(f"Only Gilgames can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")

    for member in ctx.message.guild.members:
        if member.activity is not None:
            if member.activity.name is not None:
                if member.activity.name.lower() in data["forbiddengames"]:
                    await ctx.send(f"{member.mention} stop playing {member.activity.name.lower()} (touch grass)")


# quote management
@client.command(aliases=["qm", "quotem", "qmanage"], help="Can be used to manage quotes\n"
                                                          "Operations: add, remove, list, removeall\n"
                                                          "[quotename] can only be one word")
async def quotemanage(ctx, operation="list", quotename="", *, quote=""):
    # check permission
    if str(ctx.message.author.id) not in data["whitelist"][str(ctx.message.guild.id)]:
        await ctx.send(f"Only whitelisted users can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")

    server_id = str(ctx.message.guild.id)
    if server_id not in data["quotes"]:
        data["quotes"][server_id] = {}

    if operation in ("list", "l"):
        tosend = ""
        for i in data["quotes"][server_id]:
            tosend += f'\n`{i}` by {data["quotes"][server_id][i]["author"]}'
        if tosend != "":
            await ctx.send("Quotes on this server:" + tosend)
        else:
            await ctx.send("No quotes found on this server")

    elif operation in ("clear", "c", "removeall", "rma"):
        data["quotes"].pop(server_id, None)
        save_data()
        await ctx.send("Removed every quote on the server")

    elif quotename != "":
        quotename = quotename.lower()
        if operation in ("a", "add"):
            data["quotes"][server_id][quotename] = {"author": ctx.message.author.name, "quote": quote}
            save_data()
            await ctx.send(f"Quote `{quotename}` was added")

        elif operation in ("remove", "r", "rm"):
            data["quotes"][server_id].pop(quotename, None)
            save_data()
            await ctx.send(f"Removed `{quotename}` from quotes")

        else:
            await ctx.send(f"Invalid operation")

    else:
        await ctx.send(f"Quotename cannot be empty")


# quote use
@client.command(aliases=["q"], help="Can be used to quote quotes")
async def quote(ctx, quotename):
    print(f"{ctx.message.author} called {ctx.message.content}")
    server_id = str(ctx.message.guild.id)
    quotename = quotename.lower()
    if quotename in data["quotes"][server_id]:
        await ctx.message.reply(f'As {data["quotes"][server_id][quotename]["author"]} once said:\n\n'
                                f'{data["quotes"][server_id][quotename]["quote"]}', mention_author=False)
    else:
        await ctx.message.add_reaction("🚫")


# insult add
@client.command(aliases=["iadd", "ia", "insulta"], help="Can be used to add insults")
async def addinsult(ctx, language="", *, insult=""):
    # check permission
    if await checkwhitelist(ctx):
        return
    print(f"{ctx.message.author} called {ctx.message.content}")

    if language == "":
        await ctx.send(f"Language cannot be empty")
    elif insult == "":
        await ctx.send(f"Insults cannot be empty")
    else:
        if language not in data["insults"]:
            data["insults"][language] = []
        data["insults"][language].append(insult)
        save_data()
        await ctx.message.delete()
        await ctx.send(f"Insult `{insult}` was added to `{language}`", delete_after=5)


# insult use
@client.command(aliases=["i"], help="Can be used to send insults")
async def insult(ctx, language):
    if language in data["insults"]:
        await ctx.reply(f'{ctx.author} said:\n||{random.choice(data["insults"][language])}||', mention_author=False)
    else:
        await ctx.send(f"Language `{language}` not found", )


"""@client.command(aliases=["socialcredit", "credit"], help="Helps keeping the server clean")
async def sc(ctx, operation="get", citizen: Member = None, credit=0):
    if await checkwhitelist(ctx):
        return
    serverid = str(ctx.guild.id)
    sdata = load_server(ctx.guild.id)

    if citizen is None:
        citizen = ctx.message.author
    cid = str(citizen.id)

    try:
        credit = int(credit)
    except:
        await ctx.message.reply(f"Credit must be an integer", mention_author=False, delete_after=5)
        return

    if citizen.id not in sdata["sc"]:
        sdata["sc"][cid] = 0
    score = sdata["sc"][cid]

    if operation in ("get", "g"):
        await ctx.message.reply(f'Social credit score of `{citizen.name}`: {score}', mention_author=False)
        if score > 0:
            await ctx.send("<:bingchilling:955836634102906932>")
        elif score < 0:
            await ctx.send("<:nosocialcredit:958399755095007252>")
        elif score == 0:
            await ctx.send("<:indeedcorrect:955836633561841666>")

    elif operation in ("add", "a", "change"):
        if credit > 0:
            sdata["sc"][cid] += credit
            await ctx.message.reply(f'`{citizen.name}` was given {credit} credits', mention_author=False)
            await ctx.send("<:bingchilling:955836634102906932>")
        elif credit < 0:
            sdata["sc"][cid] += credit
            await ctx.message.reply(f'`{citizen.name}` was removed {-credit} credits', mention_author=False)
            await ctx.send("<:nosocialcredit:958399755095007252>")
        elif credit == 0:
            await ctx.send("<:indeedcorrect:955836633561841666>")
        save_server(serverid, sdata)"""

client.run(token)
