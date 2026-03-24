# Nyxx-Fluxer-
My Bot for Fluxer. Originally ported from discord.py to fluxer.py

# Please dont steal my work
I worked hard for a few months to get far on my bot. This is my first ever Discord bot, and I don't want it stolen. So please, don't steal my work as I'm working hard to make a good bot.

# How to use?
?help for available commands

# Features
- General commands: help, ping, userinfo, serverinfo, rules
- Moderation commands: warn, check_warnings, reset_warnings, kick, ban, unban, timeout
- Logging: message deletions and member joins

# Porting Notes
This bot was originally written from the py-cord libs but has been ported to use fluxer.py (some of it). Key changes:
- Commands use prefix `?` instead of slash commands `/` (for the time being)
- Cog system uses fluxer's Cog class (simular to discord.py's cog)
- Moderation uses fluxer's HTTP API directly
- Events use `@Cog.listener()` decorator

# If we have problems or questions with Nyxx, how can we reach you?
- Discord: **fwdrxyy_**
- Fluxer: **fwdrxyy_#3427**
