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

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="in development"))


#automod so it all auto deletes and auto get the channle and it all automod so like bad words and stuff
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if the message contains a link
    if any(link in message.content for link in ['http://', 'https://', 'www.']):
        await message.delete()
        await message.channel.send(f"{message.author.mention}, links are not allowed in this server.")

    await bot.process_commands(message)

#bad automod 
bad_words = ['badword1', 'badword2', 'badword3']
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    if any(word in content for word in bad_words):
        await message.delete()
        await message.channel.send(f"{message.author.mention}, please refrain from using inappropriate language.")

    await bot.process_commands(message)

#welcome message
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='welcome')
    if channel:
        await channel.send(f'Welcome, {member.mention}! Enjoy your stay.')

#goodbye message
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name='goodbye')
    if channel:
        await channel.send(f'Goodbye, {member.name}! We will miss you.')

#more auto mod
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    if 'discord.gg/' in content:
        await message.delete()
        await message.channel.send(f"{message.author.mention}, invite links are not allowed in this server.")

    await bot.process_commands(message)

#more auto mod like ping the ower
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    if 'ping' in content:
        await message.channel.send(f"{message.author.mention}, please do not ping the owner.")

    await bot.process_commands(message)

































































bot.run(token)
  
  





