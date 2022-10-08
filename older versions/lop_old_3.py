from discord import *
from discord.ext import commands
import json
import os
import asyncio

# constants
gil = (954419840251199579, 890963749115150357)

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
        ddata = {"forbiddengames": [], "quotes": {}, "whitelist": {}, "messages": {}, "mutedrole": 0}
        with open(f"servers/{serverid}.json", "w") as outpoot:
            json.dump(ddata, outpoot, sort_keys=True, indent=4)
    with open(f"servers/{serverid}.json", "r") as inpoot:
        return json.load(inpoot)


async def checkwhitelist(ctx):
    sdata = load_server(ctx.guild.id)
    if str(ctx.message.author.id) not in sdata["whitelist"] and ctx.message.author.id not in gil:
        await embedfail(ctx, "Only whitelisted users can use this command")
        return True


async def checkgil(ctx):
    if ctx.message.author.id not in gil:
        await embedfail(ctx, "Only Gilgames can use this command")
        return True


async def embedfail(ctx, error):
    eembed = Embed()
    eembed.add_field(name="Error", value=error, inline=False)
    await ctx.message.reply(embed=eembed, mention_author=False, delete_after=5)


async def embedsuccess(ctx, log):
    eembed = Embed()
    eembed.add_field(name="Successfully", value=log, inline=False)
    await ctx.message.reply(embed=eembed, mention_author=False)


# when the client is ready
@client.event
async def on_ready():
    print(f"{client.user} reports for a minuscule amount of trolling")
    print(f"{round(client.latency * 100)}ms")
    await client.change_presence(activity=Activity(type=ActivityType.watching, name="Gilgames's nightmares"))


# C O M M A N D S


# WHITELIST
@client.command(aliases=["wl", "wlist"], help="Manages whitelisted user")
async def whitelist(ctx, command="l", wlmember: Member = None):
    if await checkgil(ctx):
        return
    serverid = str(ctx.guild.id)
    sdata = load_server(ctx.guild.id)

    # list whitelisted users
    if command in ("list", "l"):
        await ctx.message.reply(f'```json\n{json.dumps(sdata["whitelist"], indent=4, sort_keys=True)}```',
                                mention_author=False)

    elif wlmember is not None:
        # add user to whitelist
        if command in ("add", "promote"):
            sdata["whitelist"][str(wlmember.id)] = wlmember.name
            save_server(serverid, sdata)
            await embedsuccess(ctx, f"Added `{wlmember.name}` to the whitelist")

        # remove user from whitelist
        elif command in ("remove", "demote", "rm"):
            sdata["whitelist"].pop(str(wlmember.id), None)
            save_server(serverid, sdata)
            await embedsuccess(ctx, f"Removed `{wlmember.name}` from the whitelist")

        else:
            await embedfail(ctx, "Invalid command")
    else:
        await embedfail(ctx, "Invalid user")


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
            tosend += f'\n`{sdata["quotes"][i]["author"]}` - `{i}`'
        if tosend != "":
            await ctx.message.reply("Quotes on this server:" + tosend, mention_author=False)
        else:
            await embedfail(ctx, "No quotes were found on this server")

    elif operation in ("clear", "c", "removeall", "rma"):
        sdata["quotes"] = {}
        save_server(serverid, sdata)
        await embedsuccess(ctx, "Removed every quote on the server")

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
            save_server(serverid, sdata)
            await embedsuccess(ctx, f"Added quote: `{quotename}`")

        elif operation in ("remove", "r", "rm"):
            sdata["quotes"].pop(quotename, None)
            save_server(serverid, sdata)
            await embedsuccess(ctx, f"Removed quote: `{quotename}`")

        else:
            await embedfail(ctx, "Invalid operation")
    else:
        await embedfail(ctx, "Quotename cannot be empty")


# QUOTE USE
@client.command(aliases=["q"], help="Can be used to quote quotes")
async def quote(ctx, quotename):
    sdata = load_server(ctx.guild.id)
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
    serverid = str(ctx.guild.id)
    sdata = load_server(ctx.guild.id)

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
            save_server(serverid, sdata)
            await embedsuccess(ctx, f"Added forbidden game to list `{game}`")
        else:
            await embedfail(ctx, "Invalid game name")

    elif operation in ("remove", "rm"):
        if game != "" and game in sdata["forbiddengames"]:
            sdata["forbiddengames"].remove(game)
            save_server(serverid, sdata)
            await embedsuccess(ctx, f"Removed forbidden game from list `{game}`")
        else:
            await embedfail(ctx, "Invalid game name")

    elif operation in ("clear", "rma"):
        sdata["forbiddengames"] = []
        save_server(serverid, sdata)
        await embedsuccess(ctx, "Cleared forbidden games")

    elif operation in ("list", "l"):
        if len(sdata["forbiddengames"]) == 0:
            await embedfail(ctx, "No forbidden games were found on this server")
        else:
            await ctx.message.reply(f'```json\n{json.dumps(sdata["forbiddengames"], indent=4, sort_keys=True)}```',
                                    mention_author=False)


@client.command(aliases=["banlist", "bl"], help="Shows every banned member with ID")
async def bans(ctx, serverid=""):
    if await checkwhitelist(ctx):
        return
    if serverid == "":
        serverid = str(ctx.guild.id)

    try:
        bans = await client.get_guild(int(serverid)).bans()
    except:
        await embedfail(ctx, "Invalid ID or could not fetch server bans")
        return

    band = {}
    for ban in bans:
        band[str(ban.user.id)] = str(ban.user)
    await ctx.message.reply(f'```json\n{json.dumps(band, indent=4, sort_keys=True)}```', mention_author=False)


@client.command(help="Makes the bot say something")
async def say(ctx, *, text):
    if await checkgil(ctx):
        return
    await ctx.message.delete()
    await ctx.send(text)


@client.command(aliases=["emojis", "em"], help="Downloads server emotes")
async def emotes(ctx, serverid="", operation="send"):
    if await checkgil(ctx):
        return
    if serverid == "":
        serverid = str(ctx.guild.id)
    else:
        try:
            emotelist = client.get_guild(int(serverid)).emojis
        except:
            await embedfail(ctx, "Invalid ID or could not fetch server emojis")
            return

    for emo in emotelist:
        if operation == "send":
            await ctx.send(f"`{emo.name}`\n{emo.url_as()}")
        elif operation == "save":
            if emo.animated:
                await emo.url_as().save(f"./emotes/{emo.name}.gif")
            else:
                await emo.url_as().save(f"./emotes/{emo.name}.png")
        else:
            await embedfail(ctx, "Invalid operation")
    else:
        await embedsuccess(ctx, f"Processed all emotes from `{serverid}`")


@client.command()
async def upload(ctx):
    if await checkgil(ctx):
        return
    if ctx.message.reference is not None:
        referencemsg = await ctx.fetch_message(ctx.message.reference.message_id)
        if referencemsg.attachments:
            for attachment in referencemsg.attachments:
                await attachment.save(f"servers/{attachment.filename}")
                await embedsuccess(ctx, f"Saved file `{attachment.filename}`")
        else:
            await embedfail(ctx, "No message attachments were found")
    elif ctx.message.attachments:
        for attachment in ctx.message.attachments:
            await attachment.save(f"servers/{attachment.filename}")
            await embedsuccess(ctx, f"Saved file `{attachment.filename}`")
    else:
        await embedfail(ctx, "No message attachments were found")


@client.command()
async def download(ctx, serverid=""):
    if await checkgil(ctx):
        return
    if serverid == "":
        serverid = str(ctx.guild.id)
    try:
        await ctx.message.reply(mention_author=False, file=File(f"servers/{serverid}.json"))
    except:
        await embedfail(ctx, "Server not found")


@client.command()
@commands.has_permissions(kick_members=True)
async def ban(ctx, muser: Member, *, reason=None):
    sdata = load_server(ctx.guild.id)
    if "ban" not in sdata["messages"]:
        msg = None
    else:
        msg = sdata["messages"]["ban"]

    await muser.send(f"You have been banned from {ctx.guild.name} for the following reason:\n> {reason}")
    if msg is not None:
        await muser.send(msg)
    try:
        await muser.ban(reason=reason)
    except:
        await embedfail(ctx, f"Could not ban `{muser}`")
        return

    if msg is not None:
        await embedsuccess(ctx, f"Banned `{muser}` and sent the following message to them:")
        await ctx.send(msg)
    else:
        await embedsuccess(ctx, f"Banned `{muser}`\nReason: {reason}")


@client.command()
@commands.has_permissions(ban_members=True)
async def kick(ctx, muser: Member, *, reason=None):
    sdata = load_server(ctx.guild.id)
    if "kick" not in sdata["messages"]:
        msg = None
    else:
        msg = sdata["messages"]["kick"]

    await muser.send(f"You have been kicked from {ctx.guild.name} for the following reason:\n> {reason}")
    if msg is not None:
        await muser.send(msg)
    try:
        await muser.kick(reason=reason)
    except:
        await embedfail(ctx, f"Could not kick `{muser}`")
        return

    if msg is not None:
        await embedsuccess(ctx, f"Kicked `{muser}` and sent the following message to them:")
        await ctx.send(msg)
    else:
        await embedsuccess(ctx, f"Kicked `{muser}`\nReason: {reason}")


@client.command(aliases=["msg", "message", "messages"])
async def dm(ctx, event, *, msg=""):
    if await checkwhitelist(ctx):
        return
    serverid = str(ctx.guild.id)
    sdata = load_server(ctx.guild.id)
    if msg == "":
        if event in sdata["messages"]:
            await ctx.message.reply(sdata["messages"][event], mention_author=False)
        else:
            await embedfail(ctx, f"No `{event}` message found")

    elif event in ("ban", "kick", "mute"):
        sdata["messages"][event] = msg
        save_server(serverid, sdata)
        await embedsuccess(ctx, f"Changed the `{event}` message to `{msg}`")

    else:
        await embedfail(ctx, f"Invalid operation or unexpected error")


@client.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, muser: Member, *, reason=None):
    sdata = load_server(ctx.guild.id)
    if "mute" not in sdata["messages"]:
        msg = None
    else:
        msg = sdata["messages"]["mute"]

    try:
        mutedur = int(reason.split(" ")[0])
        stripreason = ""
        for i in reason.split(" ")[1:]:
            stripreason += i + " "
        reason = stripreason
    except:
        mutedur = 0

    if ctx.author.top_role.position > ctx.guild.get_member(client.user.id).top_role.position:
        if sdata["mutedrole"] != 0:
            mrole = utils.get(ctx.guild.roles, id=sdata["mutedrole"])
            clientuser = ctx.guild.get_member(client.user.id)
            if muser.top_role.position >= clientuser.top_role.position:
                await embedfail(ctx, f"Nice argument, however, it appears that {muser.mention} has a higher rank role")
                return
            elif mrole.position >= clientuser.top_role.position:
                await embedfail(ctx, f"My rank is not high enough to assign <@&{mrole.id}>")
                return
            else:
                await muser.add_roles(mrole)
                await embedsuccess(ctx, f"Muted {muser.mention}\nReason: {reason}\nDuration: {mutedur} minutes")
        else:
            await embedfail(ctx, f"No muted role found, set it up using `,mutedrole <@mutedrole>`")
            return
    else:
        await embedfail(ctx, f"Nice argument, however, it appears that I have a higher rank role")
        return

    await muser.send(f"You have been muted in {ctx.guild.name} for the following reason:\n> {reason}")
    if msg is not None:
        await muser.send(msg)

    if mutedur != 0:
        await asyncio.sleep(mutedur * 60)
        await muser.remove_roles(utils.get(ctx.guild.roles, id=sdata["mutedrole"]))


@client.command(aliases=["muterole", "mrole"])
async def mutedrole(ctx, mrole: Role):
    if await checkwhitelist(ctx):
        return
    serverid = str(ctx.guild.id)
    sdata = load_server(ctx.guild.id)

    sdata["mutedrole"] = mrole.id
    save_server(serverid, sdata)
    await embedsuccess(ctx, f"Updated the muted role to <@&{mrole.id}>")


client.run(token)
