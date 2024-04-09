import discord
from discord.ext import commands
import os 
from keep_alive import keep_alive
keep_alive()
import random
import asyncio
import sqlite3

# Define your developer IDs here
developer_ids = ['719648115639975946', '719648115639975946', '719648115639975946']

token = os.environ['token']

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="in development"))
  
#ping command
@bot.command(name='ping')
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f'Pong! Latency: **{round(latency * 1000)}**ms')

developer_role_id = 1222641922049445920  # Replace with your developer role ID
announcement_channel_name = "announcement"  # Replace with the name of the announcement channel

@bot.command(name='announce', help='Announce a message to developers only')
async def announce(ctx, *, message):
    """Announce a message to developers only."""
    if any(role.id == developer_role_id for role in ctx.author.roles):
        for guild in bot.guilds:
            announcement_channel = discord.utils.get(guild.channels, name=announcement_channel_name, type=discord.ChannelType.text)
            if announcement_channel:
                await announcement_channel.send(f"📢 **Developer Announcement:** {message}")
        await ctx.send("Announcement sent to all servers.")
    else:
        await ctx.send("You do not have permission to use this command.")




































































bot.run(token)
  
  





