import re
import fluxer
from fluxer import Cog

class General(Cog):
    def __init__(self, bot):
        super().__init__(bot)

    @Cog.command()
    async def help(self, ctx):
        """List all available commands"""
        commands_list = [f"?{cmd} - {getattr(handler, '__doc__', 'No description') or 'No description'}" for cmd, handler in self.bot._commands.items()]
        await ctx.reply("# Available commands:\n" + "\n".join(commands_list))

    @Cog.command()
    async def ping(self, ctx):
        #fluxer doesn't have latency tracking like discord.py. hopefully this will be added in the future, but for now we can just reply with "Pong!"
        """Pong! Checks if the bot is responsive as a test command."""
        await ctx.reply("Pong!")

    def _resolve_target(self, ctx, member):
        # Default to command author
        if not member:
            return ctx.author

        # Accept direct mention or ID string
        if isinstance(member, str):
            member_id = None
            mention_match = re.search(r"<@!?([0-9]+)>", member)
            if mention_match:
                member_id = int(mention_match.group(1))
            elif member.isdigit():
                member_id = int(member)

            if member_id is not None:
                try:
                    return self.bot.fetch_user(member_id)
                except Exception:
                    return member

        return member

    @Cog.command()
    async def userinfo(self, ctx, member=None):
        """Display information about a user."""
        if isinstance(member, str) and member.isdigit():
            member = int(member)

        if isinstance(member, int):
            try:
                member_obj = await self.bot.fetch_user(member)
                member = member_obj
            except Exception:
                pass

        member = await self._resolve_target(ctx, member)

        data_user = None
        join_date = "Unknown"

        if hasattr(member, "user"):
            data_user = member.user
            join_date = getattr(member, "joined_at", "Unknown")
        elif hasattr(member, "username") or hasattr(member, "display_name"):
            data_user = member
            join_date = getattr(member, "created_at", "Unknown")
        elif hasattr(member, "id"):
            data_user = member

        if not data_user:
            await ctx.reply("Could not resolve user data for userinfo.")
            return

        name = getattr(data_user, "display_name", None) or getattr(data_user, "username", None) or getattr(data_user, "name", None) or "Unknown"
        user_id = getattr(data_user, "id", "Unknown")

        info = f"Name: {name}\nID: {user_id}\nJoined: {join_date}"
        await ctx.reply(info)

    @Cog.command()
    async def serverinfo(self, ctx):
        """Display information about the server."""
        guild = getattr(ctx, 'guild', None)

        # Fallback if context guild is missing, try message channel guild_id
        if not guild:
            channel = getattr(ctx, 'channel', None)
            guild_id = getattr(channel, 'guild_id', None) if channel else None
            if guild_id and self.bot:
                try:
                    guild = await self.bot.fetch_guild(guild_id)
                except Exception:
                    guild = None

        if not guild:
            await ctx.reply("This command can only be used in a server.")
            return

        guild_name = getattr(guild, 'name', None)
        guild_id = getattr(guild, 'id', 'Unknown')
        member_count = getattr(guild, 'member_count', 'Unknown')

        # If name is missing because guild object is partial, fetch full guild
        if not guild_name and self.bot and guild_id != 'Unknown':
            try:
                refreshed = await self.bot.fetch_guild(guild_id)
                if refreshed:
                    guild_name = getattr(refreshed, 'name', guild_name)
                    member_count = getattr(refreshed, 'member_count', member_count)
            except Exception:
                pass

        guild_name = guild_name or 'Unknown Server'
        member_count = member_count or 'Unknown'

        info = f"Name: {guild_name}\nID: {guild_id}\nMembers: {member_count}"
        await ctx.reply(info)

    @Cog.command()
    async def rules(self, ctx):
        """Shows the server rules."""
        rules = [
            "1. All text channels are English only.",
            "2. No harassment.",
            # Add more rules as needed
        ]
        await ctx.reply("\n".join(rules))