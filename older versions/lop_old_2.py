from discord import *
from discord.ext import commands
import json

# initialization
fnj = "lop_data.json"
client = commands.Bot(command_prefix=",")
token = "token"
gil = 465376961284276236
with open(fnj, "r") as read_file:
    data = json.load(read_file)
whitell = []
for wl in data["whitelist"]:
    whitell.append(int(wl["userid"]))

triggers = {"channels": [], "users": [], "keywords": []}
for i in data["reactions"][0]["channels"]:
    triggers["channels"].append(int(i["id"]))
for i in data["reactions"][0]["users"]:
    triggers["users"].append(int(i["id"]))
for i in data["reactions"][0]["keywords"]:
    triggers["keywords"].append(i["id"])


# function to save the data
def save_data():
    with open(fnj, "w+") as fp:
        json.dump(data, fp, sort_keys=True, indent=4)


# when the client is ready
@client.event
async def on_ready():
    print(f"{client.user} reports for a minuscule amount of trolling")
    print(f"{round(client.latency * 100)}ms")
    await client.change_presence(activity=Activity(type=ActivityType.watching, name="Gilgames's nightmares"))


# runs for every message
@client.event
async def on_message(message):
    await client.process_commands(message)
    channelid = message.channel.id
    auth = message.author

    # i dont recommend doing this
    async def respond(i):
        if i["type"] == "emote":
            await message.add_reaction(i["reply"])
            print(f'reacted with {i["reply"]} in #{message.channel}')

        elif i["type"] == "reply":
            await message.reply(i["reply"], mention_author=False)
            print(f'replied with {i["reply"]} in #{message.channel}')

    if auth != client.user:
        if client.user.mentioned_in(message):
            message.reply(data["info"], mention_author=False)

        # channel
        if channelid in triggers["channels"]:
            for i in data["reactions"][0]["channels"]:
                if i["id"] == channelid:
                    await respond(i)

        # user
        if auth.id in triggers["users"]:
            for i in data["reactions"][0]["users"]:
                if i["id"] == auth.id:
                    await respond(i)

        # keyword
        for i in data["reactions"][0]["keywords"]:
            if i["id"].lower() in message.content.lower():
                await respond(i)


# COMMANDS


# whitelist management
@client.command(aliases=["wl", "wlist"], help="Manages whitelisted user")
async def whitelist(ctx, command="l", iid=0):
    # check GIL
    if ctx.message.author.id != gil:
        await ctx.send(f"Only Gilgames can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")

    global whitell

    # list whitelisted users
    if command in ("list", "l"):
        await ctx.send(f'```json\n{json.dumps(data["whitelist"], indent=4, sort_keys=True)}```')

    # add user to whitelist
    elif command in ("add", "promote"):
        wuser = await client.fetch_user(int(iid))
        if iid != 0 and wuser is not None:
            whitell.append(iid)
            data["whitelist"].append({"name": wuser.name, "userid": iid})
            save_data()
            await ctx.send(f"{wuser.name} has been added to the whitelist")
        else:
            await ctx.send(f"Failed to add user to whitelist")

    # remove user from whitelist
    elif command in ("remove", "demote", "rm"):
        wuser = await client.fetch_user(int(iid))
        if iid != 0 and wuser is not None:

            for i in range(len(data["whitelist"])):
                if data["whitelist"][i]["userid"] == iid:
                    del data["whitelist"][i]
                    whitell.remove(iid)
                    break
            else:
                await ctx.send(f"User could not be found on the whitelist")
                return
            save_data()
            await ctx.send(f"{wuser.name} has been removed from the whitelist")
        else:
            await ctx.send(f"Failed to remove user from whitelist")


# latency
@client.command(help="Returns the client's latency")
async def ping(ctx):
    if ctx.message.author.id not in whitell:
        await ctx.send(f"Only whitelisted users can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")
    await ctx.send(f"{round(client.latency * 100)}ms")


# bulk delete any amount of messages
@client.command(aliases=["purge", "cls"], help="Deletes a certain amount of messages")
async def clear(ctx, amount=2):
    if ctx.message.author.id not in whitell:
        await ctx.send(f"Only whitelisted users can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")
    if ctx.message.author.id != gil:
        await ctx.send(f"Only Gilgames can use this command")
        return

    await ctx.channel.purge(limit=amount)


# make the bot say something
@client.command(help="Makes the bot say something")
async def say(ctx, *, text):
    if ctx.message.author.id != gil:
        await ctx.send(f"Only Gilgames can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")
    await ctx.message.delete()
    await ctx.send(text)


# better reactions and triggers
@client.command(aliases=["t"], help="Manages keywords, channels and users the bot will react with a reply or an emote "
                                    "later to\nOperations: list, add, remove, clear")
async def trigger(ctx, operation="list", server_id=0, channel_id=0, trigger_type="everything", trigger_spec="",
                  reply_type="reply", reply="🗿"):
    # check permission
    if ctx.message.author.id not in whitell:
        await ctx.send(f"Only whitelisted users can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")

    # check if server is valid
    try:
        server_id = int(server_id)
    except:
        await ctx.send(f"Invalid channel ID")
        return
    if server_id == 0:
        server_id = ctx.guild.id
    elif client.get_guild(server_id) is None:
        await ctx.send(f"Invalid channel ID")
    # check if channel is valid
    try:
        channel_id = int(channel_id)
    except:
        await ctx.send(f"Invalid channel ID")
        return
    if channel_id == 0:
        channel_id = ctx.channel.id
    elif client.get_channel(channel_id) is None:
        await ctx.send(f"Invalid channel ID")

    # used
    # functions

    # determine trigger type
    async def determine_trigger_type():
        nonlocal trigger_spec
        nonlocal trigger_type
        # users
        if trigger_type in ("user", "u", "member", "users"):
            # check if user is valid
            try:
                trigger_spec = int(trigger_spec)
            except:
                await ctx.send(f"Invalid user ID")
                return
            if trigger_spec == 0:
                trigger_spec = ctx.message.author.id
            auth = await client.fetch_user(trigger_spec)
            if auth is None:
                await ctx.send(f"Invalid user ID")
                return
            return "users"

        # keywords
        elif trigger_type in ("key", "keyword", "k", "keywords"):
            return "keywords"

        else:
            return

    # determine operation
    if operation in ("add", "a"):
        dtype = await determine_trigger_type()
        try:
            data["triggers"][str(server_id)][str(channel_id)][dtype][str(trigger_spec)].append(
                {"type": reply_type, "reply": reply})
            print("try")
        except:
            data.update({"triggers": {
                server_id: {channel_id: {dtype: {str(trigger_spec): [{"type": reply_type, "reply": reply}]}}}}})
            print("exc")

        save_data()
        await ctx.send(f"Successfully added\n`key: {trigger_spec}\ntype: {reply_type}\nreply: {reply}`")

    elif operation in ("remove", "r", "rm"):
        del data["triggers"][str(server_id)][str(channel_id)][determine_trigger_type()][trigger_spec]
        await ctx.send(f"Successfully removed\n`key: {trigger_spec}`")

    elif operation in ("list", "l"):
        try:
            await ctx.send(f'```json\n{json.dumps(data["triggers"][str(server_id)], indent=4, sort_keys=True)}```')
        except:
            await ctx.send("No triggers found in the server")

    elif operation in ("clearchannel", "cc"):
        data["triggers"][str(server_id)].pop(str(channel_id), None)
        save_data()
        await ctx.send(f"Successfully cleared every trigger in\n`{channel_id}`")

    elif operation in ("clearserver", "cs"):
        data["triggers"].pop(str(server_id), None)
        save_data()
        await ctx.send(f"Successfully cleared every trigger in\n`{server_id}`")

    else:
        await ctx.send("Invalid operation")


# reactions management
@client.command(aliases=["reaction", "reply", "r"], help="Manages keywords, channels and users the bot "
                                                         "will react with a reply or an emote later to\n"
                                                         "Operations: list, add, remove, clear")
async def react(ctx, operation="list", command="l", ertype="reply", discord_id="0", *, reply="🗿"):
    # check permission
    if ctx.message.author.id not in whitell:
        await ctx.send(f"Only whitelisted users can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")
    # allow access to outer scope
    global triggers

    if ertype in ("reply", "r", "answer", "text"):
        ertype = "reply"
    elif ertype in ("emote", "emoji", "e", "reaction"):
        ertype = "emote"
    else:
        await ctx.send(f"Ivalid form, use `reply` or `emote`")
        return

    # determines whether the command is channel, user, or keywords, returns "" if none of these
    async def determine_ctype():
        # allow access to outer scope, but only inside this function
        nonlocal discord_id

        if command in ("channel", "ch", "c", "channels"):
            discord_id = int(discord_id)
            if discord_id == 0:
                discord_id = ctx.channel.id
            if client.get_channel(discord_id) is None:
                await ctx.send(f"Invalid ID")
                return None
            return "channels"

        elif command in ("user", "u", "member", "users"):
            discord_id = int(discord_id)
            if discord_id == 0:
                discord_id = ctx.message.author
            auth = await client.fetch_user(discord_id)
            if auth is None:
                await ctx.send(f"Invalid ID")
                return None
            return "users"

        elif command in ("key", "keyword", "k", "keywords"):
            return "keywords"

        else:
            return ""

    # add a trigger entry
    async def add_trigger(ct, tid):
        triggers[ct].append(tid)
        data["reactions"][0][ct].append({"id": tid, "type": ertype, "reply": reply})
        save_data()
        await ctx.send(f"Successfully added\n`id: {tid}\ntype: {ertype}\nreply: {reply}`")

    # remove one trigger entry
    async def remove_trigger(ct, tid):
        for i in range(len(data["reactions"][0][ct])):
            if data["reactions"][0][ct][i]["id"] == tid:
                await ctx.send(f"Successfully removed\n`id: {tid}`")
                del data["reactions"][0][ct][i]
                triggers[ct].remove(tid)
                save_data()
                break
        else:
            await ctx.send(f"Invalid channel")

    # clear every trigger entry
    async def clear_trigger(ct):
        triggers[ct] = []
        data["reactions"][0][ct] = []
        save_data()
        await ctx.send(f"Successfully cleared\n`{ct}`")

    async def list_trigger(ct):
        await ctx.send(f'```json\n{json.dumps(data["reactions"][0][ct], indent=4, sort_keys=True)}```')

    ctype = await determine_ctype()

    # CHECK COMMAND
    if ctype != "":
        # check operation
        if operation in ("add", "a"):
            await add_trigger(ctype, discord_id)

        elif operation in ("remove", "r", "rm"):
            await remove_trigger(ctype, discord_id)

        elif operation in ("list", "l"):
            await list_trigger(ctype)

        elif operation in ("clear", "rma", "removeall"):
            await clear_trigger(ctype)

    # list everything
    elif command in ("list", "l"):
        await ctx.send(f'```json\n{json.dumps(data["reactions"][0], indent=4, sort_keys=True)}```')

    # remove everything
    elif command in ("clear", "rma", "removeall"):
        await clear_trigger("channels")
        await clear_trigger("users")
        await clear_trigger("keywords")
        save_data()

    else:
        await ctx.send(f"Invalid command")


@client.command(help="Makes a backup of the last given amount of messages in the current channel\n"
                     "Commands: all, media, emotes, pins, bans, embeds")
async def backup(ctx, command, discord_id, amount=5):
    if ctx.message.author.id not in whitell:
        await ctx.send(f"Only whitelisted users can use this command")
        return
    print(f"{ctx.message.author} called {ctx.message.content}")

    if command in ("all", "everything", "*"):
        source_channel = client.get_channel(int(discord_id))
        async for msg in source_channel.history(limit=amount, oldest_first=True):
            await ctx.send(f"{msg.author}\n{msg.content}")
            if msg.attachments:
                for att in msg.attachments:
                    await ctx.send(f"{att.url}")

    elif command in ("media", "images"):
        source_channel = client.get_channel(int(discord_id))
        async for msg in source_channel.history(limit=amount, oldest_first=True):
            if msg.embeds:
                for emb in msg.embeds:
                    await ctx.send(f"{msg.author}\n{emb.url}")
            if msg.attachments:
                for att in msg.attachments:
                    await ctx.send(f"{msg.author}\n{att.url}")

    elif command in ("emote", "emotes", "emoji", "emojis"):
        server = client.get_guild(int(discord_id))
        for emo in server.emojis:
            await ctx.send(f"{emo.name}\n{emo.url_as()}")

    elif command in ("pin", "pinned", "pins"):
        server = client.get_guild(int(discord_id))
        for tc in server.text_channels:
            pins = await tc.pins()
            if len(pins) != 0:
                await ctx.send(f"**{tc.name}**")
                for pin in pins:
                    await ctx.send(f"{pin.author}\n{pin.content}")
                    if pin.attachments:
                        for att in pin.attachments:
                            await ctx.send(f"{att.url}")

    elif command in ("ban", "bans", "banned", "banneds"):
        server = client.get_guild(int(discord_id))
        bans = await server.bans()
        for ban in bans:
            await ctx.send(f"`{ban.user.id}`: {ban.user.name} ")

    elif command in ("embed", "embeds"):
        source_channel = client.get_channel(int(discord_id))
        async for msg in source_channel.history(limit=amount, oldest_first=True):
            if msg.embeds:
                for emb in msg.embeds:
                    await ctx.send(embed=emb.copy())

    else:
        await ctx.send(f"Invalid argument")


client.run(token)
