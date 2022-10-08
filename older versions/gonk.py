from discord import *
from discord.ext import commands
import json
import random
import os
import requests

# admins
admin = (954419840251199579, 728894475740512286)

# initialization
# keep_alive()
secret_token = os.environ['token']
intents = Intents.default()
intents.presences = True
intents.members = True
client = commands.Bot(command_prefix=',', intents=intents)


# necessary functions
def save_server(ddata):
    with open(f"save_data.json", "w+") as outpoot:
        json.dump(ddata, outpoot, sort_keys=True, indent=4)


def load_server():
    with open(f"save_data.json", "r") as inpoot:
        return json.load(inpoot)


async def checkwhitelist(ctx):
    sdata = load_server()
    if str(ctx.message.author.id) not in sdata["whitelist"] and ctx.message.author.id not in admin:
        await embedfail(ctx, "Only whitelisted users can use this command")
        return True


async def checkadmin(ctx):
    if ctx.message.author.id not in admin:
        await embedfail(ctx, "Only bot admins can use this command")
        return True


async def embedfail(ctx, error):
    eembed = Embed()
    eembed.add_field(name="Error", value=error, inline=False)
    await ctx.message.reply(embed=eembed, mention_author=False)


async def embedsuccess(ctx, log):
    eembed = Embed()
    eembed.add_field(name="Successfully", value=log, inline=False)
    await ctx.message.reply(embed=eembed, mention_author=False)


async def embedreply(ctx, title, msg):
    eembed = Embed()
    eembed.add_field(name=title, value=msg, inline=False)
    await ctx.message.reply(embed=eembed, mention_author=False)


trigger_keys = []


# when the client is ready
@client.event
async def on_ready():
    sdata = load_server()
    global trigger_keys
    trigger_keys = sdata["triggers"]
    print(f"{client.user} reports for a minuscule amount of trolling")
    print(f"{round(client.latency * 100)}ms")
    # await client.change_presence(activity=Activity(type=ActivityType.watching, name="Gilgames's nightmares"))


# on message
@client.event
async def on_message(message):
    await client.process_commands(message)
    ctx = await client.get_context(message)
    auth = message.author
    content = message.content.lower()

    if auth != client.user:
        # dadjoke
        if (content.startswith("im ") or content.startswith("i am ") or content.startswith("i'm ")) and len(
                content) < 50:
            immsg = message.content.replace("im ", "")
            immsg = immsg.replace("i am ", "")
            immsg = immsg.replace("i'm ", "")
            await ctx.message.reply(f"Hi {immsg}, I'm <@972110590149525584>", mention_author=False)

        # trigger
        for i in trigger_keys:
            if i in content:
                if trigger_keys[i]["type"] == "emote":
                    await message.add_reaction(trigger_keys[i]["reply"])
                elif trigger_keys[i]["type"] == "reply":
                    await message.reply(trigger_keys[i]["reply"], mention_author=False)


# C O M M A N D S


# WHITELIST
@client.command(aliases=["wl", "wlist"], help="Manages whitelisted user")
async def whitelist(ctx, command="l", wlmember: Member = None):
    if await checkadmin(ctx):
        return
    sdata = load_server()

    # list whitelisted users
    if command in ("list", "l"):
        await ctx.message.reply(f'```json\n{json.dumps(sdata["whitelist"], indent=4, sort_keys=True)}```',
                                mention_author=False)

    elif wlmember is not None:
        # add user to whitelist
        if command in ("add", "promote"):
            sdata["whitelist"][str(wlmember.id)] = wlmember.name
            save_server(sdata)
            await embedsuccess(ctx, f"Added `{wlmember.name}` to the whitelist")

        # remove user from whitelist
        elif command in ("remove", "demote", "rm"):
            sdata["whitelist"].pop(str(wlmember.id), None)
            save_server(sdata)
            await embedsuccess(ctx, f"Removed `{wlmember.name}` from the whitelist")

        else:
            await embedfail(ctx, "Invalid command")
    else:
        await embedfail(ctx, "Invalid user")


# CLEAR
@client.command(aliases=["purge", "cls"], help="Deletes a certain amount of messages")
async def clear(ctx, amount=1):
    if await checkadmin(ctx):
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

    sdata = load_server()

    if operation in ("list", "l"):
        if len(sdata["quotes"]) == 0:
            await embedfail(ctx, "No quotes were found on this server")
            return

        tosend = ""
        lines = 0
        pages = 1

        for i in sdata["quotes"]:
            tosend += i + "\n"
            lines += 1
            if lines == 10:
                eembed = Embed()
                eembed.add_field(name="Quotes", value=tosend, inline=False)
                eembed.set_footer(text=f"Page {pages}")
                await ctx.send(embed=eembed, mention_author=False)
                tosend = ""
                lines = 0
                pages += 1
        if lines != 0:
            eembed = Embed()
            eembed.add_field(name="Quotes", value=tosend, inline=False)
            eembed.set_footer(text=f"Page {pages}")
            await ctx.send(embed=eembed, mention_author=False)

    elif quotename != "":
        quotename = quotename.lower()
        if operation in ("a", "add"):
            if ctx.message.reference is not None and quote == "":
                referencemsg = await ctx.fetch_message(ctx.message.reference.message_id)
                refcontent = referencemsg.content
                if referencemsg.attachments:
                    for att in referencemsg.attachments:
                        refcontent += f"\n{att.url}"
                sdata["quotes"][quotename] = {"author": referencemsg.author.id, "quote": refcontent.strip("\n")}

            else:
                sdata["quotes"][quotename] = {"author": ctx.message.author.id, "quote": quote}
            save_server(sdata)
            await embedsuccess(ctx, f"Added quote: `{quotename}`")

        elif operation in ("remove", "r", "rm"):
            sdata["quotes"].pop(quotename, None)
            save_server(sdata)
            await embedsuccess(ctx, f"Removed quote: `{quotename}`")

        else:
            await embedfail(ctx, "Invalid operation")
    else:
        await embedfail(ctx, "Quotename cannot be empty")


# QUOTE USE
@client.command(aliases=["q"], help="Can be used to quote quotes")
async def quote(ctx, quotename):
    sdata = load_server()
    quotename = quotename.lower()

    if quotename in sdata["quotes"]:
        qquote = sdata["quotes"][quotename]["quote"]
        qembed = Embed()
        try:
            auth = await client.fetch_user(int(sdata["quotes"][quotename]["author"]))
            qembed.set_author(name=str(auth), icon_url=auth.avatar_url)
            qauth = auth.display_name
        except:
            qauth = sdata["quotes"][quotename]["author"]
            qembed.set_author(name=qauth)

        links = []
        if "https://" in qquote:
            aquote = qquote.split(" ")
            qquote = ""
            for w in range(len(aquote)):
                if aquote[w].startswith("https://"):
                    links.append(aquote[w])
                    qquote += "[link] "
                else:
                    qquote += aquote[w] + " "

        qembed.add_field(name=f"As {qauth} once said: ", value=qquote, inline=False)

        qembed.set_footer(text=quotename)
        await ctx.message.reply(mention_author=False, embed=qembed)
        if links is not []:
            qcontent = ""
            for i in links:
                qcontent += i + "\n"
            if qcontent != "":
                await ctx.send(qcontent)
    else:
        await embedfail(ctx, f"Quote `{quotename}` not found")


# FORBIDDENGAMES
@client.command(aliases=["touchgrass", "shower", "fgames", "fg", "grass"], help="Warns members playing forbidden games"
                                                                                "\nOperations: warn, add, remove, clear"
                                                                                ", list")
async def forbiddengames(ctx, operation="warn", *, game=""):
    if await checkwhitelist(ctx):
        return
    sdata = load_server()

    game = game.lower()
    if operation in ("warn", "w"):
        for member in ctx.guild.members:
            if member.activity is not None:
                if member.activity.name is not None:
                    if (game == "" and member.activity.name.lower() in sdata["forbiddengames"]) or \
                            (game != "" and member.activity.name.lower() == game):
                        await ctx.send(f"{member.mention} touch grass, stop playing {member.activity.name}")

    elif operation in ("add", "a"):
        if game != "":
            sdata["forbiddengames"].append(game)
            save_server(sdata)
            await embedsuccess(ctx, f"Added forbidden game to list `{game}`")
        else:
            await embedfail(ctx, "Invalid game name")

    elif operation in ("remove", "rm"):
        if game != "" and game in sdata["forbiddengames"]:
            sdata["forbiddengames"].remove(game)
            save_server(sdata)
            await embedsuccess(ctx, f"Removed forbidden game from list `{game}`")
        else:
            await embedfail(ctx, "Invalid game name")

    elif operation in ("list", "l"):
        if len(sdata["forbiddengames"]) == 0:
            await embedfail(ctx, "No forbidden games were found on this server")
        else:
            await ctx.message.reply(f'```json\n{json.dumps(sdata["forbiddengames"], indent=4, sort_keys=True)}```',
                                    mention_author=False)

    else:
        await embedfail(ctx, "Invalid operation")


# say
@client.command(help="Makes the bot say something")
async def say(ctx, *, text):
    if await checkadmin(ctx):
        return
    await ctx.message.delete()
    await ctx.send(text)


# trigger
@client.command(aliases=["t"], help="Manages keywords that trigger custom responses")
async def trigger(ctx, operation="list", keyword="", reply_type="reply", *, reply="🗿"):
    if await checkadmin(ctx):
        return
    sdata = load_server()
    keyword = keyword.lower()
    global trigger_keys

    if operation in ("list", "l"):
        if len(sdata["triggers"]) == 0:
            await embedfail(ctx, "No keywords were found on this server")
            return

        tosend = ""
        lines = 0
        pages = 1

        for i in sdata["triggers"]:
            tosend += i + "\n"
            lines += 1
            if lines == 10:
                eembed = Embed()
                eembed.add_field(name="Keywords", value=tosend, inline=False)
                eembed.set_footer(text=f"Page {pages}")
                await ctx.send(embed=eembed, mention_author=False)
                tosend = ""
                lines = 0
                pages += 1
        if lines != 0:
            eembed = Embed()
            eembed.add_field(name="Keywords", value=tosend, inline=False)
            eembed.set_footer(text=f"Page {pages}")
            await ctx.send(embed=eembed, mention_author=False)

    elif operation in ("add", "a"):
        if keyword != "" and reply_type in ("reply", "emote"):
            sdata["triggers"][keyword] = {"type": reply_type, "reply": reply}
            save_server(sdata)
            trigger_keys = sdata["triggers"]
            await embedsuccess(ctx, f"Added `{keyword}` to the list")
        else:
            await embedfail(ctx, "Invalid command")

    elif operation in ("remove", "rm"):
        if keyword != "" and keyword in sdata["triggers"]:
            sdata["triggers"].pop(keyword, None)
            save_server(sdata)
            trigger_keys = sdata["triggers"]
            await embedsuccess(ctx, f"Removed `{keyword}` from the list")
        else:
            await embedfail(ctx, "Invalid keyword")

    else:
        await embedfail(ctx, "Invalid operation")


# by Bronski

def randommod():
    mods = [
        "Perse",
        "Újság",
        "Acrazit",
        "Rudi",
        "Bence",
        "Ananas",
        "Kuta",
        "Levante",
        "oogr",
        "Le Meme Man",
        "Gilgames"
    ]
    return random.choice(mods)


@client.command(help="Returns a quote by the mods")
async def modquote(ctx):
    req = requests.get("https://free-quotes-api.herokuapp.com/").text
    await ctx.message.reply(f"*{json.loads(req)['quote']}* - {randommod()}", mention_author=False)


@client.command(help="Returns a fact about the mods")
async def fact(ctx):
    req = requests.get('https://api.chucknorris.io/jokes/random')
    await ctx.message.reply(json.loads(req.content)["value"].replace("Chuck Norris", randommod()), mention_author=False)


@client.command(aliases=["1984"], help="Reminds you on the famous book of George Orwell")
async def literally(ctx):
    await ctx.message.reply(
        "https://cdn.discordapp.com/attachments/951139521808982076/952472743683711046/1984_moment-1.mp4"
        , mention_author=False)


client.run(secret_token)
