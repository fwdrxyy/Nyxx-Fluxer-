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

    @Cog.command()
    async def userinfo(self, ctx, member=None):
        """Display information about a user."""
        member = member or ctx.author
        info = f"Name: {member.name}\nID: {member.id}\nJoined: {member.joined_at}"
        await ctx.reply(info)

    @Cog.command()
    async def serverinfo(self, ctx):
        """Display information about the server."""
        guild = ctx.guild
        if guild:
            info = f"Name: {guild.name}\nID: {guild.id}\nMembers: {guild.member_count}"
            await ctx.reply(info)
        else:
            await ctx.reply("This command can only be used in a server.")

    @Cog.command()
    async def rules(self, ctx):
        """Shows the server rules."""
        rules = [
            "1. All text channels are English only.",
            "2. No harassment.",
            # Add more rules as needed
        ]
        await ctx.reply("\n".join(rules))