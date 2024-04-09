import discord
from discord.ext import commands
import os 
from keep_alive import keep_alive
keep_alive()
import random
# Define your developer IDs here
developer_ids = ['719648115639975946', '719648115639975946', '719648115639975946']
developer_role_id = 1222641922049445920
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

@bot.command(name='announce', help='Announce a message to developers only')
async def announce(ctx, *, message):
    """Announce a message to developers only."""
    if any(role.id == developer_role_id for role in ctx.author.roles):
        developer_role = discord.utils.get(ctx.guild.roles, id=developer_role_id)
        await developer_role.send(f"📢 **Developer Announcement:** {message}")
        await ctx.send("Announcement sent to developers.")
    else:
        await ctx.send("You do not have permission to use this command.")











bot.run(token)
  
  





