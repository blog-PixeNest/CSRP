import discord
from discord.ext import commands
import os 
from keep_alive import keep_alive
keep_alive()
import random
import asyncio
import sqlite3
from discord_slash import SlashCommand


# Define your developer IDs here
developer_ids = ['719648115639975946', '719648115639975946', '719648115639975946']

token = os.environ['token']

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())
slash = SlashCommand(bot, sync_commands=True)  # Declares slash commands through the bot.

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="in development"))

@slash.slash(name="hello", description="Says hello!")
async def _hello(ctx):
    await ctx.send("Hello!")

@slash.slash(name="roll", description="Rolls a dice")
async def _roll(ctx, sides: int):
    import random
    result = random.randint(1, sides)
    await ctx.send(f'You rolled a {result} (1-{sides}).')
  




































































bot.run(token)
  
  





