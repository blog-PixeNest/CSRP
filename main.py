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


#ban command and the eorror mssage
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason):
    try:
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned for {reason}.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to ban members.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to ban the member.")

#kick command and the eorror mssage
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason):
    try:
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked for {reason}.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to kick members.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to kick the member.")  

#mute/timeout command and the eorror mssage
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int, *, reason):
    try:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f'{member.mention} has been muted for {duration} seconds for {reason}.')

        await asyncio.sleep(duration)
        await member.remove_roles(muted_role, reason="Mute duration expired.")
        await ctx.send(f'{member.mention} has been unmuted.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage roles or assign the Muted role.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to mute the member.")

#unmute/untimeout command and the eorror mssage
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    try:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f'{member.mention} has been unmuted.')
        else:
            await ctx.send(f'{member.mention} is not muted.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage roles or remove the Muted role.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to unmute the member.")

#clear command and the eorror mssage
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    try:
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'{amount} messages have been cleared.', delete_after=5)
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage messages.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to clear messages.")

#warn command and the eorror mssage and saves the warns in a db like sqlite3
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('warns.db')
        c = conn.cursor()

        # Create the warns table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS warns (
                        user_id INTEGER,
                        reason TEXT,
                        timestamp TEXT
                    )''')

        # Insert the warn into the database
        c.execute("INSERT INTO warns (user_id, reason, timestamp) VALUES (?, ?, ?)",
                  (member.id, reason, str(ctx.message.created_at)))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        await ctx.send(f'{member.mention} has been warned for {reason}.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage messages.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to warn the member.")

#warns command and the eorror mssage
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warns(ctx, member: discord.Member):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('warns.db')
        c = conn.cursor()

        # Retrieve the warns for the member from the database
        c.execute("SELECT reason, timestamp FROM warns WHERE user_id=?", (member.id,))
        warns = c.fetchall()

        if warns:
            warn_list = "\n".join([f"{index + 1}. {warn[0]} - {warn[1]}" for index, warn in enumerate(warns)])
            await ctx.send(f'Warns for {member.mention}:\n{warn_list}')
        else:
            await ctx.send(f'{member.mention} has no warns.')

        # Close the connection
        conn.close()
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage messages.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to retrieve warns for the member.")

#removewarn/unwarn command and the eorror mssage
@bot.command()
@commands.has_permissions(manage_messages=True)
async def unwarn(ctx, member: discord.Member, warn_index: int):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('warns.db')
        c = conn.cursor()

        # Retrieve the warn from the database
        c.execute("SELECT reason, timestamp FROM warns WHERE user_id=? AND rowid=?", (member.id, warn_index))
        warn = c.fetchone()

        if warn:
            # Remove the warn from the database
            c.execute("DELETE FROM warns WHERE user_id=? AND rowid=?", (member.id, warn_index))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

            await ctx.send(f'Warn {warn_index} for {member.mention} has been removed.')
        else:
            await ctx.send(f'Warn {warn_index} for {member.mention} does not exist.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage messages.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to remove the warn.")

#more moderation commands

#unban command and the eorror mssag
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, member_id: int):
    try:
        user = await bot.fetch_user(member_id)
        await ctx.guild.unban(user)
        await ctx.send(f'{user.name} has been unbanned.')
    except discord.NotFound:
        await ctx.send("User not found.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to unban members.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to unban the member.")

#lock/unlock command and the eorror mssage
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f'{channel.mention} has been locked.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage channels.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to lock the channel.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    try:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f'{channel.mention} has been unlocked.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage channels.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to unlock the channel.")

#fun commands and the eorror mssage

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency: {latency}ms')

@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)

@bot.command()
async def roll(ctx, sides: int = 6):
    result = random.randint(1, sides)
    await ctx.send(f'You rolled a {result} on a {sides}-sided dice!')

@bot.command()
async def flip(ctx):
    result = random.choice(['Heads', 'Tails'])
    await ctx.send(f'The coin landed on {result}!')

@bot.command()
async def choose(ctx, *options):
    if len(options) < 2:
        await ctx.send("Please provide at least two options.")
    else:
        chosen_option = random.choice(options)
        await ctx.send(f'I choose: {chosen_option}')

@bot.command()
async def coinflip(ctx):
    result = random.choice(['Heads', 'Tails'])
    await ctx.send(f'The coin landed on {result}!')

@bot.command()
async def rps(ctx, choice: str):
    choices = ['rock', 'paper', 'scissors']
    bot_choice = random.choice(choices)

    if choice not in choices:
        await ctx.send("Invalid choice. Please choose either 'rock', 'paper', or 'scissors'.")
        return

    if choice == bot_choice:
        await ctx.send(f"It's a tie! Both chose {choice}.")
    elif (choice == 'rock' and bot_choice == 'scissors') or (choice == 'paper' and bot_choice == 'rock') or (choice == 'scissors' and bot_choice == 'paper'):
        await ctx.send(f"You win! You chose {choice} and I chose {bot_choice}.")
    else:
        await ctx.send(f"I win! I chose {bot_choice} and you chose {choice}.")

@bot.command()
async def gayrate(ctx, member: discord.Member = None):  
    if member is None:
        member = ctx.author
    gay_percentage = random.randint(0, 100000)
    await ctx.send(f'{member.mention} is {gay_percentage}% gay!')

@bot.command()
async def simprate(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    simp_percentage = random.randint(0, 100)
    await ctx.send(f'{member.mention} is {simp_percentage}% simp!')

@bot.command()
async def pp(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    pp_length = random.randint(0, 20)
    pp_string = '8' + '=' * pp_length + 'D'
    await ctx.send(f'{member.mention}\'s pp size is {pp_string}')


#cmd to get all commands 
@bot.command()
async def cmd(ctx):
    command_list = [command.name for command in bot.commands]
    await ctx.send(f"Available commands: {', '.join(command_list)}")













































































bot.run(token)
  
  





