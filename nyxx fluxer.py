import fluxer
import os
from dotenv import load_dotenv

bot = fluxer.Bot(command_prefix="?", intents=fluxer.Intents.default())

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user.username}")

@bot.command()
async def ping(ctx):
    await ctx.reply("Pong!")



load_dotenv()
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)