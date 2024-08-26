import discord
# TODO: make cache expire
webhook_cache = {}

async def get_webhook(channel, bot = None):
    if channel.id in webhook_cache:
        return webhook_cache[channel.id]
    
    if not bot:
        return None
    
    webhooks = await channel.webhooks()

    # check if theres a valid webhook already we can use
    for webhook in webhooks:
        if webhook.name == "LopFeed":
            webhook_cache[channel.id] = webhook
            return webhook
    else:
        webhook = await channel.create_webhook(name="LopFeed")
        webhooks = await channel.webhooks()
        webhook_cache[channel.id] = webhook
        return webhook
    
async def threadhook_send(channel, bot, message, username, avatar_url):
    if isinstance(channel, discord.Thread):
        # specify thread
        webhook = await get_webhook(channel.parent, bot)
        await webhook.send(message, username=username, avatar_url=avatar_url, thread=channel)
    else:
        webhook = await get_webhook(channel, bot)
        await webhook.send(message, username=username, avatar_url=avatar_url)