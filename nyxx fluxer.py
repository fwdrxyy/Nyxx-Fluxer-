import fluxer
import os
import asyncio
from dotenv import load_dotenv
from fluxer.enums import ChannelType
from fluxer.models.channel import Channel

bot = fluxer.Bot(command_prefix="?", intents=fluxer.Intents.default())

# Import cogs
from cogs.General import General
from cogs.Moderation import Moderation

# Load cogs
async def load_cogs():
    await bot.add_cog(General(bot))
    await bot.add_cog(Moderation(bot))

# Logging functions
async def find_log_channel(guild):
    log_channel_names = ["logs", "mod-log"]

    # Discord-style API object may have text_channels attribute.
    if hasattr(guild, "text_channels"):
        for channel in guild.text_channels:
            if channel and channel.name and any(name in channel.name.lower() for name in log_channel_names):
                return channel

    # Fluxer Guild object may not cache channels; fetch from API.
    if guild._http:
        channels_data = await guild._http.get_guild_channels(guild.id)
    elif bot._http:
        channels_data = await bot._http.get_guild_channels(guild.id)
    else:
        return None

    for cdata in channels_data:
        if cdata.get("type") == ChannelType.GUILD_TEXT and cdata.get("name"):
            lname = cdata["name"].lower()
            if any(name in lname for name in log_channel_names):
                channel = Channel.from_data(cdata, bot._http)
                channel._guild = guild
                return channel

    return None

@bot.event
async def on_message_delete(data):
    # Fluxer dispatches raw event payload dictionaries for MESSAGE_DELETE
    guild_id = int(data.get("guild_id")) if data.get("guild_id") else None
    if guild_id is None:
        return

    guild = bot._guilds.get(guild_id)
    if not guild:
        return

    log_channel = await find_log_channel(guild)
    if log_channel:
        author_id = data.get("author", {}).get("id") if isinstance(data.get("author"), dict) else None
        author_name = None
        if author_id:
            try:
                author_obj = await bot.fetch_user(author_id)
                author_name = author_obj.username if author_obj else str(author_id)
            except Exception:
                author_name = str(author_id)

        content = data.get("content") or "[No Content]"
        username = author_name or "Unknown user"
        await log_channel.send(f"Message deleted ({data.get('id', 'unknown')}): {username}: {content}")

@bot.event
async def on_member_join(data):
    # Fluxer dispatches raw payload dictionaries for GUILD_MEMBER_ADD
    guild_id = int(data.get("guild_id")) if data.get("guild_id") else None
    user_data = data.get("user") if isinstance(data.get("user"), dict) else None

    if guild_id is None or not user_data:
        return

    guild = bot._guilds.get(guild_id)
    if not guild:
        return

    log_channel = await find_log_channel(guild)
    if log_channel:
        name = user_data.get("username", "Unknown")
        await log_channel.send(f"{name} has joined the server.")


# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

async def main():
    await load_cogs()
    if TOKEN:
        await bot.start(TOKEN)
    else:
        print("No TOKEN environment variable found!")

if __name__ == "__main__":
    try:
        if not asyncio.get_event_loop().is_running():
            asyncio.run(main())
        else:
            # Running in existing event loop (e.g. notebook or hosted container)
            try:
                import nest_asyncio
            except ImportError:
                raise
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            loop.create_task(main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            try:
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                loop.create_task(main())
            except ImportError:
                raise
        else:
            raise