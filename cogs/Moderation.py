import re
import fluxer
from fluxer import Cog
import sqlite3
import datetime

class Moderation(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.db_path = "warnings.db"
        self.init_db()

    def _resolve_member_id(self, member_identifier):
        if hasattr(member_identifier, "id"):
            return int(member_identifier.id)

        if isinstance(member_identifier, int):
            return member_identifier

        if isinstance(member_identifier, str):
            # Support mention formats: <@123>, <@!123>
            mention_match = re.search(r"<@!?([0-9]+)>", member_identifier)
            if mention_match:
                return int(mention_match.group(1))

            # Support raw numeric snowflake string
            if member_identifier.isdigit():
                return int(member_identifier)

        raise ValueError("Unable to resolve member id from identifier")

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER PRIMARY KEY,
                warning_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def get_warnings(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT warning_count FROM warnings WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0

    def add_warning(self, user_id):
        count = self.get_warnings(user_id) + 1
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO warnings (user_id, warning_count) VALUES (?, ?)', (user_id, count))
        conn.commit()
        conn.close()
        return count

    def reset_warnings(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE warnings SET warning_count = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    @Cog.command()
    async def warn(self, ctx, member, *, reason: str = "No reason provided"):
        """Warn a user"""
        try:
            member_id = self._resolve_member_id(member)
        except ValueError as e:
            await ctx.reply(str(e))
            return
        if not ctx.guild:
            await ctx.reply("This command can only be used in a server.")
            return

        try:
            # Get member object
            member = await self.bot.fetch_user(member_id)
            if not member:
                await ctx.reply("User not found.")
                return

            count = self.add_warning(member_id)

            username = member.display_name if hasattr(member, 'display_name') else (getattr(member, 'username', str(member_id)))

            # Check if user should be timed out or banned
            if count >= 5:
                # Ban when 5+ warnings (order changed to ensure 5 is honored before 3?)
                await self.bot._http.ban_guild_member(ctx.guild.id, member_id, reason=f"Auto-ban: {count} warnings")
                await ctx.reply(f"{username} has been warned ({count} warnings) and banned.")
            elif count >= 3:
                # Timeout for 1 hour
                until = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()
                await self.bot._http.timeout_guild_member(ctx.guild.id, member_id, until=until, reason=f"Auto-timeout: {count} warnings")
                await ctx.reply(f"{username} has been warned ({count} warnings) and timed out for 1 hour.")
            else:
                await ctx.reply(f"{username} has been warned ({count} warnings). Reason: {reason}")

        except Exception as e:
            await ctx.reply(f"Error warning user: {e}")

    @Cog.command()
    async def check_warnings(self, ctx, member):
        """Check a user's warnings"""
        try:
            member_id = self._resolve_member_id(member)
        except ValueError as e:
            await ctx.reply(str(e))
            return

        count = self.get_warnings(member_id)
        user = await self.bot.fetch_user(member_id)
        name = user.name if user else f"User {member_id}"
        await ctx.reply(f"{name} has {count} warnings.")

    @Cog.command()
    async def reset_warnings(self, ctx, member):
        """Reset a user's warnings"""
        try:
            member_id = self._resolve_member_id(member)
        except ValueError as e:
            await ctx.reply(str(e))
            return

        self.reset_warnings(member_id)
        user = await self.bot.fetch_user(member_id)
        name = user.name if user else f"User {member_id}"
        await ctx.reply(f"Reset warnings for {name}.")

    @Cog.command()
    async def kick(self, ctx, member, *, reason: str = "No reason provided"):
        """Kick a user"""
        if not ctx.guild:
            await ctx.reply("This command can only be used in a server.")
            return

        try:
            member_id = self._resolve_member_id(member)
        except ValueError as e:
            await ctx.reply(str(e))
            return

        try:
            await self.bot._http.kick_guild_member(ctx.guild.id, member_id, reason=reason)
            user = await self.bot.fetch_user(member_id)
            name = user.display_name if user and hasattr(user, 'display_name') else (user.username if user else f"User {member_id}")
            await ctx.reply(f"Kicked {name}. Reason: {reason}")
        except Exception as e:
            await ctx.reply(f"Error kicking user: {e}")

    @Cog.command()
    async def ban(self, ctx, member, *, reason: str = "No reason provided"):
        """Ban a user"""
        if not ctx.guild:
            await ctx.reply("This command can only be used in a server.")
            return

        try:
            member_id = self._resolve_member_id(member)
        except ValueError as e:
            await ctx.reply(str(e))
            return

        try:
            await self.bot._http.ban_guild_member(ctx.guild.id, member_id, reason=reason)
            user = await self.bot.fetch_user(member_id)
            name = user.display_name if user and hasattr(user, 'display_name') else (user.username if user else f"User {member_id}")
            await ctx.reply(f"Banned {name}. Reason: {reason}")
        except Exception as e:
            await ctx.reply(f"Error banning user: {e}")

    @Cog.command()
    async def unban(self, ctx, member, *, reason: str = "No reason provided"):
        """Unban a user"""
        if not ctx.guild:
            await ctx.reply("This command can only be used in a server.")
            return

        try:
            member_id = self._resolve_member_id(member)
        except ValueError as e:
            await ctx.reply(str(e))
            return

        try:
            await self.bot._http.unban_guild_member(ctx.guild.id, member_id, reason=reason)
            user = await self.bot.fetch_user(member_id)
            name = user.display_name if user and hasattr(user, 'display_name') else (user.username if user else f"User {member_id}")
            await ctx.reply(f"Unbanned {name}. Reason: {reason}")
        except Exception as e:
            await ctx.reply(f"Error unbanning user: {e}")

    @Cog.command()
    async def timeout(self, ctx, member_id: int, hours: int = 1, reason: str = "No reason provided"):
        """Timeout a user for specified time (in hours)"""
        if not ctx.guild:
            await ctx.reply("This command can only be used in a server.")
            return

        try:
            until = (datetime.datetime.utcnow() + datetime.timedelta(hours=hours)).isoformat()
            await self.bot._http.timeout_guild_member(ctx.guild.id, member_id, until=until, reason=reason)
            user = await self.bot.fetch_user(member_id)
            name = user.name if user else f"User {member_id}"
            await ctx.reply(f"Timed out {name} for {hours} hours. Reason: {reason}")
        except Exception as e:
            await ctx.reply(f"Error timing out user: {e}")