from discord import *
from discord.ext import commands
import json
import datetime
import random
import os

# constants
gil = (954419840251199579, 890963749115150357)
fnj = "lop_data.json"

# initialization
with open("token.txt", "r") as tokenfile:
    for line in tokenfile:
        token = line
        break

intents = Intents.default()
intents.presences = True
intents.members = True
client = commands.Bot(command_prefix=',', intents=intents)


# necessary functions
def save_server(serverid, ddata):
    with open(f"servers/{serverid}.json", "w+") as outpoot:
        json.dump(ddata, outpoot, sort_keys=True, indent=4)


def load_server(serverid):
    if not os.path.exists(f"servers/{serverid}.json"):
        ddata = {"bdate": {}, "forbiddengames": [], "insult": {}, "quotes": {}, "whitelist": {}, "sc": {}}
        with open(f"servers/{serverid}.json", "w") as outpoot:
            json.dump(ddata, outpoot, sort_keys=True, indent=4)
    with open(f"servers/{serverid}.json", "r") as inpoot:
        return json.load(inpoot)


async def checkwhitelist(ctx):
    sdata = load_server(ctx.guild.id)
    if str(ctx.message.author.id) not in sdata["whitelist"] and ctx.message.author.id not in gil:
        await ctx.message.reply(f"Only whitelisted users can use this command", mention_author=False, delete_after=5)
        return True
    print(f"{ctx.message.author} called {ctx.message.content}")


async def checkgil(ctx):
    if ctx.message.author.id not in gil:
        await ctx.message.reply(f"Only Gilgames can use this command", mention_author=False, delete_after=5)
        return True
    print(f"{ctx.message.author} called {ctx.message.content}")


# when the client is ready
@client.event
async def on_ready():
    print(f"{client.user} reports for a minuscule amount of trolling")
    print(f"{round(client.latency * 100)}ms")
    await client.change_presence(activity=Activity(type=ActivityType.watching, name="Gilgames's nightmares"))


# C O M M A N D S


# WHITELIST
@client.command(aliases=["wl", "wlist"], help="Manages whitelisted user")
async def whitelist(ctx, command="l", iid=0):
    if await checkgil(ctx):
        return

    serverid = str(ctx.guild.id)
    sdata = load_server(ctx.guild.id)

    # list whitelisted users
    if command in ("list", "l"):
        await ctx.message.reply(f'```json\n{json.dumps(sdata["whitelist"], indent=4, sort_keys=True)}```',
                                mention_author=False)

    else:
        try:
            iid = int(iid)
            wuser = await client.fetch_user(iid)
            if wuser is None:
                await ctx.message.reply(f"Invalid user ID", mention_author=False, delete_after=5)
                return
        except:
            await ctx.message.reply(f"Invalid user ID (ID must be an integer)", mention_author=False, delete_after=5)
            return

        # add user to whitelist
        if command in ("add", "promote"):
            sdata["whitelist"][str(iid)] = wuser.name
            save_server(serverid, sdata)
            await ctx.message.reply(f"{wuser.name} has been added to the whitelist", mention_author=False)

        # remove user from whitelist
        elif command in ("remove", "demote", "rm"):
            sdata["whitelist"].pop(str(iid), None)
            save_server(serverid, sdata)
            await ctx.message.reply(f"{wuser.name} has been removed from the whitelist", mention_author=False)

        else:
            await ctx.message.reply(f"Invalid command", mention_author=False, delete_after=5)


# CLEAR
@client.command(aliases=["purge", "cls"], help="Deletes a certain amount of messages")
async def clear(ctx, amount=1):
    if await checkgil(ctx):
        return
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)


# QUOTE MANAGE
@client.command(aliases=["qm", "quotem", "qmanage"], help="Can be used to manage quotes\n"
                                                          "Operations: add, remove, list, removeall\n"
                                                          "[quotename] can only be one word")
async def quotemanage(ctx, operation="list", quotename="", *, quote=""):
    if await checkwhitelist(ctx):
        return

    serverid = str(ctx.guild.id)
    sdata = load_server(ctx.guild.id)

    if operation in ("list", "l"):
        tosend = ""
        for i in sdata["quotes"]:
            tosend += f'\n`{i}` by {sdata["quotes"][i]["author"]}'
        if tosend != "":
            await ctx.send("Quotes on this server:" + tosend)
        else:
            await ctx.message.reply("No quotes found on this server", mention_author=False)

    elif operation in ("clear", "c", "removeall", "rma"):
        sdata["quotes"] = {}
        save_server(serverid, sdata)
        await ctx.message.reply("Removed every quote on the server", mention_author=False)

    elif quotename != "":
        quotename = quotename.lower()
        if operation in ("a", "add"):
            if ctx.message.reference is not None and quote == "":
                referencemsg = await ctx.fetch_message(ctx.message.reference.message_id)
                refcontent = referencemsg.content
                if referencemsg.attachments:
                    for att in referencemsg.attachments:
                        refcontent += f"\n{att.url}"
                sdata["quotes"][quotename] = {"author": referencemsg.author.name, "quote": refcontent.strip("\n")}

            else:
                sdata["quotes"][quotename] = {"author": ctx.message.author.name, "quote": quote}
            save_server(serverid, sdata)
            await ctx.message.reply(f"Quote `{quotename}` was added", mention_author=False)

        elif operation in ("remove", "r", "rm"):
            sdata["quotes"].pop(quotename, None)
            save_server(serverid, sdata)
            await ctx.message.reply(f"Removed `{quotename}` from quotes", mention_author=False)

        else:
            await ctx.message.reply(f"Invalid operation", mention_author=False, delete_after=5)

    else:
        await ctx.message.reply(f"Quotename cannot be empty", mention_author=False, delete_after=5)


# QUOTE USE
@client.command(aliases=["q"], help="Can be used to quote quotes")
async def quote(ctx, quotename):
    print(f"{ctx.message.author} called {ctx.message.content}")
    sdata = load_server(ctx.guild.id)
    quotename = quotename.lower()
    if quotename in sdata["quotes"]:
        await ctx.message.reply(f'As {sdata["quotes"][quotename]["author"]} once said:\n\n'
                                f'{sdata["quotes"][quotename]["quote"]}', mention_author=False)
    else:
        await ctx.message.add_reaction("🚫")


# FORBIDDENGAMES
@client.command(aliases=["touchgrass", "shower", "fgames", "fg", "grass"], help="Warns members playing forbidden games"
                                                                                "\nOperations: warn, add, remove, clear"
                                                                                ", list")
async def forbiddengames(ctx, operation="warn", *, game=""):
    if await checkwhitelist(ctx):
        return
    serverid = str(ctx.guild.id)
    sdata = load_server(ctx.guild.id)

    game = game.lower()
    if operation in ("warn", "w"):
        for member in ctx.guild.members:
            if member.activity is not None:
                if member.activity.name is not None:
                    if (game == "" and member.activity.name.lower() in sdata["forbiddengames"]) or \
                            (game != "" and member.activity.name.lower() == game):
                        await ctx.send(f"{member.mention} touch grass, stop playing {member.activity.name.lower()}")

    elif operation in ("add", "a"):
        if game != "":
            sdata["forbiddengames"].append(game)
            save_server(serverid, sdata)
            await ctx.message.reply(f"Added forbidden game to list `{game}`", mention_author=False)
        else:
            await ctx.message.reply(f"Invalid game name", mention_author=False, delete_after=5)

    elif operation in ("remove", "rm"):
        if game != "" and game in sdata["forbiddengames"]:
            sdata["forbiddengames"].remove(game)
            save_server(serverid, sdata)
            await ctx.message.reply(f"Removed forbidden game from list `{game}`", mention_author=False)
        else:
            await ctx.message.reply(f"Invalid game name", mention_author=False, delete_after=5)

    elif operation in ("clear", "rma"):
        sdata["forbiddengames"] = []
        save_server(serverid, sdata)
        await ctx.message.reply(f"Cleared forbidden games", mention_author=False)

    elif operation in ("list", "l"):
        if len(sdata["forbiddengames"]) == 0:
            await ctx.message.reply("No forbidden games found on this server", mention_author=False)
        else:
            await ctx.message.reply(f'```json\n{json.dumps(sdata["forbiddengames"], indent=4, sort_keys=True)}```',
                                    mention_author=False)


@client.command(aliases=["banlist", "bl"], help="Shows every banned member with ID")
async def bans(ctx, serverid=""):
    if await checkwhitelist(ctx):
        return
    if serverid == "":
        serverid = str(ctx.guild.id)
    else:
        try:
            bans = await client.get_guild(int(serverid)).bans()
        except:
            await ctx.message.reply(f"Error or invalid ID", mention_author=False, delete_after=5)
            return

    band = {}
    for ban in bans:
        band[str(ban.user.id)] = ban.user.name
    await ctx.message.reply(f'```json\n{json.dumps(band, indent=4, sort_keys=True)}```', mention_author=False)


@client.command(help="Makes the bot say something")
async def say(ctx, *, text):
    if await checkgil(ctx):
        return
    await ctx.message.delete()
    await ctx.send(text)


client.run(token)
