import discord
from discord.ext import commands
import os 
from keep_alive import keep_alive
keep_alive()
import random
import asyncio
import sqlite3
import requests



# Define your developer IDs here
developer_ids = ['719648115639975946', '719648115639975946', '719648115639975946']

token = os.environ['token']



intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True


bot = commands.Bot(command_prefix='!', intents=intents)
#bot is on/status
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="in development/!botcommands"))

#sends a message to the channel when the bot joins a server
@bot.event
async def on_guild_join(guild):
    channel = guild.system_channel
    if channel is not None:
        await channel.send(f'Thanks for adding me to {guild.name}!')

#sends a message to the channel when the bot leaves a server
@bot.event
async def on_guild_remove(guild):
    channel = guild.system_channel
    if channel is not None:
        await channel.send(f'I was removed from {guild.name}.')

@bot.event
async def on_guild_join(guild):
    channel = bot.get_channel(1229123471708262451)
    if channel:
        await channel.send(f'Bot added to server: {guild.name}')
        await channel.send(f'Server ID: {guild.id}')
        await channel.send(f'Server owner: {guild.owner}')
        await channel.send(f'Member count: {guild.member_count}')

# Replace with your chosen AI provider's function
def generate_ai_response(prompt):
    #  You'll customize this based on your chosen API
    api_url = "https://mivra.onrender.com" 
    api_key = os.getenv('AI_API_KEY')  
    headers = {'Authorization': f'Bearer {api_key}'}
    data = {'prompt': prompt}

    response = requests.post(api_url, headers=headers, json=data)
    response.raise_for_status()  # Check for errors
    return response.json()['text']  # Adjust response parsing if needed



# Connect to your database
conn = sqlite3.connect('moderation.db')  
cursor = conn.cursor()

# Create the mod_actions table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mod_actions (
        server_id INTEGER,
        user_id INTEGER,
        action_type TEXT,
        reason TEXT
    )
''')
conn.commit()

# Ban command with reason storage
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't ban yourself!")
        return

    server_id = ctx.guild.id
    user_id = member.id

    cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?)", (server_id, user_id, 'ban', reason))
    conn.commit()

    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention} (ID: {user_id}). Reason: {reason}')

# Kick command with reason storage
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't kick yourself!")
        return

    server_id = ctx.guild.id
    user_id = member.id

    cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?)", (server_id, user_id, 'kick', reason))
    conn.commit()

    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention} (ID: {user_id}). Reason: {reason}')

#unban command with reason storage  
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason=None):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f'Unbanned {user.name} (ID: {user_id}). Reason: {reason}')

        server_id = ctx.guild.id
        cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?)", (server_id, user_id, 'unban', reason))
        conn.commit()
    except discord.NotFound:
        await ctx.send("User not found or not banned.")

#mute/timeout command with reason storage
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't mute yourself!")
        return

    server_id = ctx.guild.id
    user_id = member.id

    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False)

    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f'Muted {member.mention} (ID: {user_id}). Reason: {reason}')

    cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?)", (server_id, user_id, 'mute', reason))
    conn.commit()

    await asyncio.sleep(duration * 60)
    await member.remove_roles(mute_role, reason="Mute duration expired for member: " + member.name)

#unmute command with reason storage
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't unmute yourself!")
        return

    server_id = ctx.guild.id
    user_id = member.id

    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role in member.roles:
        await member.remove_roles(mute_role, reason=reason)
        await ctx.send(f'Unmuted {member.mention} (ID: {user_id}). Reason: {reason}')

        cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?)", (server_id, user_id, 'unmute', reason))
        conn.commit()
    else:
        await ctx.send(f'{member.mention} is not muted.')

#purge command with reason storage
@bot.command()
@commands.has_permissions(manage_messages=True)
async def c(ctx, amount: int, *, reason=None):
    if amount <= 0:
        await ctx.send("Please provide a valid number of messages to delete.")
        return

    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'Deleted {amount} messages. Reason: {reason}')

    server_id = ctx.guild.id
    cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?)", (server_id, ctx.author.id, 'purge', reason))
    conn.commit()

#warn command with reason storage
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You can't warn yourself!")
        return

    server_id = ctx.guild.id
    user_id = member.id

    cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?)", (server_id, user_id, 'warn', reason))
    conn.commit()

    await ctx.send(f'Warned {member.mention} (ID: {user_id}). Reason: {reason}')

#warnings command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warnings(ctx, member: discord.Member):
    server_id = ctx.guild.id
    user_id = member.id

    cursor.execute("SELECT * FROM mod_actions WHERE server_id=? AND user_id=?", (server_id, user_id))
    actions = cursor.fetchall()

    if not actions:
        await ctx.send(f'No warnings found for {member.mention} (ID: {user_id}).')
        return

    embed = discord.Embed(title=f'Warnings for {member.name} (ID: {user_id})', color=discord.Color.red())
    for action in actions:
        embed.add_field(name=f'Action: {action[2]}', value=f'Reason: {action[3]}', inline=False)

    await ctx.send(embed=embed)

#clearwarnings command 
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearwarnings(ctx, member: discord.Member):
    server_id = ctx.guild.id
    user_id = member.id

    cursor.execute("DELETE FROM mod_actions WHERE server_id=? AND user_id=?", (server_id, user_id))
    conn.commit()

    await ctx.send(f'Cleared all warnings for {member.mention} (ID: {user_id}).')

#lockdown command
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send('Server is now in lockdown. Only administrators can send messages.')

#unlock command
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send('Server is no longer in lockdown. All members can send messages.')

#serverinfo command
@bot.command()
async def serverinfo(ctx):
    server = ctx.guild
    embed = discord.Embed(title=f'Server Information - {server.name}', color=discord.Color.blue())
    embed.set_thumbnail(url=server.icon_url)
    embed.add_field(name='Server ID', value=server.id, inline=False)
    embed.add_field(name='Owner', value=server.owner.mention, inline=False)
    embed.add_field(name='Region', value=server.region, inline=False)
    embed.add_field(name='Member Count', value=server.member_count, inline=False)
    embed.add_field(name='Creation Date', value=server.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
    await ctx.send(embed=embed)

#userinfo command
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f'User Information - {member.name}', color=discord.Color.green())
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name='User ID', value=member.id, inline=False)
    embed.add_field(name='Nickname', value=member.nick, inline=False)
    embed.add_field(name='Joined Server', value=member.joined_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
    embed.add_field(name='Account Created', value=member.created_at.strftime('%Y-%m-%d %H:%M:%S'), inline=False)
    await ctx.send(embed=embed)

#avatar command
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f'Avatar - {member.name}', color=discord.Color.orange())
    embed.set_image(url=member.avatar_url)
    await ctx.send(embed=embed)


#nick command and reason storage
@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, new_nickname=None):
    if new_nickname is None:
        await member.edit(nick=None)
        await ctx.send(f'Nickname removed for {member.mention}.')
    else:
        await member.edit(nick=new_nickname)
        await ctx.send(f'Nickname changed for {member.mention} to {new_nickname}.')

    server_id = ctx.guild.id
    user_id = member.id

    cursor.execute("INSERT INTO mod_actions VALUES (?, ?, ?, ?)", (server_id, user_id, 'nick', new_nickname))
    conn.commit()

#games/fun command 

# echo command 
@bot.command()
@commands.has_permissions(manage_messages=True)
async def echo(ctx, *, message):
    await ctx.send(message)

#rps command 
@bot.command()
async def rps(ctx, choice: str):
    choices = ['rock', 'paper', 'scissors']
    bot_choice = random.choice(choices)

    if choice not in choices:
        await ctx.send('Invalid choice. Please choose either "rock", "paper", or "scissors".')
        return

    if choice == bot_choice:
        result = 'It\'s a tie!'
    elif (choice == 'rock' and bot_choice == 'scissors') or (choice == 'paper' and bot_choice == 'rock') or (choice == 'scissors' and bot_choice == 'paper'):
        result = 'You win!'
    else:
        result = 'You lose!'

    await ctx.send(f'You chose {choice}. I chose {bot_choice}. {result}')

#8ball command
@bot.command()
async def eightball(ctx, *, question):
    responses ="It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
    response = random.choice(responses)
    await ctx.send(f'Question: {question}\nAnswer: {response}')

#coinflip command
@bot.command()
async def coinflip(ctx):
    result = random.choice(['Heads', 'Tails'])
    await ctx.send(f'The coin landed on {result}!')

#roll command
@bot.command()
async def roll(ctx, sides: int = 6):
    if sides < 1:
        await ctx.send("The number of sides must be at least 1.")
        return

    result = random.randint(1, sides)
    await ctx.send(f'You rolled a {result} on a {sides}-sided die!')

#cat command
@bot.command()
async def cat(ctx):
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    data = response.json()
    image_url = data[0]['url']
    await ctx.send(image_url)

#dog command
@bot.command()
async def dog(ctx):
    response = requests.get('https://dog.ceo/api/breeds/image/random')
    data = response.json()
    image_url = data['message']
    await ctx.send(image_url)

#meme command
@bot.command()
async def meme(ctx):
    response = requests.get('https://api.imgflip.com/get_memes')
    data = response.json()
    meme = random.choice(data['data']['memes'])
    meme_url = meme['url']
    await ctx.send(meme_url)

#joke command
@bot.command()
async def joke(ctx):
    response = requests.get('https://official-joke-api.appspot.com/random_joke')
    data = response.json()
    setup = data['setup']
    punchline = data['punchline']
    await ctx.send(f'{setup}\n{punchline}')

#quote command  
@bot.command()
async def quote(ctx):
    response = requests.get('https://api.quotable.io/random')
    data = response.json()
    quote = data['content']
    author = data['author']
    await ctx.send(f'"{quote}" - {author}')

#game commands

#tictactoe command
@bot.command()
async def tictactoe(ctx, opponent: discord.Member):
    if opponent == ctx.author:
        await ctx.send("You can't play against yourself!")
        return

    if opponent.bot:
        await ctx.send("You can't play against a bot!")
        return

    player1 = ctx.author
    player2 = opponent
    board = [' ' for _ in range(9)]
    current_player = player1
    game_over = False
    def print_board():
        row1 = f'| {board[0]} | {board[1]} | {board[2]} |'
        row2 = f'| {board[3]} | {board[4]} | {board[5]} |'
        row3 = f'| {board[6]} | {board[7]} | {board[8]} |'
        separator = '-------------'
        message = f'{row1}\n{separator}\n{row2}\n{separator}\n{row3}'
        return message
    def check_win():
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]  # diagonals
        ]
        for combination in winning_combinations:
            if board[combination[0]] == board[combination[1]] == board[combination[2]] != ' ':
                return True
        return False
    def check_tie():
        return ' ' not in board
    async def make_move(position):
        nonlocal current_player
        nonlocal game_over
        if board[position] == ' ' and not game_over:
            board[position] = 'X' if current_player == player1 else 'O'
            await ctx.send(print_board())
            if check_win():
                await ctx.send(f'{current_player.mention} wins!')
                game_over = True
            elif check_tie():
                await ctx.send('It\'s a tie!')
                game_over = True
            else:
                current_player = player2 if current_player == player1 else player1
    await ctx.send(f'{player1.mention} vs {player2.mention}\n{print_board()}')
    while not game_over:
        try:
            move = await bot.wait_for('message', check=lambda m: m.author == current_player and m.channel == ctx.channel, timeout=30.0)
            position = int(move.content) - 1
            await make_move(position)
        except asyncio.TimeoutError:
            await ctx.send(f'{current_player.mention} took too long to make a move. Game over.')
            game_over = True
        except ValueError:
            await ctx.send('Invalid move. Please enter a number between 1 and 9.')

#botcommands and it a drop down menu for the cateogry the commands falls under
@bot.command()
async def botcommands(ctx):
    embed = discord.Embed(title="Bot Commands", description="Here are the available commands for the bot:", color=discord.Color.blue())
    embed.add_field(name="commands", value="`!warn <member> [reason]` - Warn a member\n`!warnings <member>` - View warnings for a member\n`!clearwarnings <member>` - Clear all warnings for a member\n`!lock` - Lock the server\n`!unlock` - Unlock the server\n`!nick <member> [new_nickname]` - Change the nickname of a member\n`!echo [message]` - Make the bot say something\n`!rps [choice]` - Play rock-paper-sissors with the bot\n`!eightball [question]` - Ask the magic 8-ball a question\n`!coinflip` - Flip a coin\n`!roll [sides]` - Roll a die\n`!cat` - Get a random cat picture\n`!dog` - Get a random dog picture\n`!meme` - Get a random meme\n`!joke` - Get a random joke\n`!quote` - Get a random quote\n`!tictactoe <opponent>` - Play tic-tac-toe with another member\n`!botcommands` - Show this menu\n`!modlog` - View the moderation log\n`!ban <member_id(can get from !modlog)> [reason]` - Ban a member\n`!unban <member>` - Unban a member\n`!kick <member> [reason]` - Kick a member\n`!mute <member> [reason]` - Mute a member\n`!unmute <member>` - Unmute a member", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def listservers(ctx):  # ctx represents the command invocation's context
    """Lists servers the bot is in along with owner IDs."""

    # Build an embed for nicer message formatting
    embed = discord.Embed(title="Server List", color=discord.Color.blue())

    for guild in bot.guilds:
        embed.add_field(name=guild.name, value=f"ID: {guild.id}, Owner ID: {guild.owner_id}", inline=False)

    await ctx.send(embed=embed)
    

@bot.command()  # Use the bot.command decorator
async def ask(ctx, *, question):  # Use ctx for context
    try:
        ai_response = generate_ai_response(question)
        await ctx.send(ai_response)
    except Exception as e:
        await ctx.send(f"Oops! Something went wrong. Error: {e}")

         
           
                
              
              
  
  














@bot.command()
@commands.has_permissions(manage_guild=True)
async def modlog(ctx, limit=10):
    server_id = ctx.guild.id
    actions = cursor.execute("SELECT action_type, user_id, reason FROM mod_actions WHERE server_id=? ORDER BY rowid DESC LIMIT ?", (server_id, limit)).fetchall()

    if actions:
        msg = "**Recent Moderation Actions:**\n"
        for action_type, user_id, reason in actions:
            try:
                user = await bot.fetch_user(user_id)
                msg += f"- {action_type.capitalize()}: {user.mention} (ID: {user_id})"
                if reason:
                    msg += f" - Reason: {reason}\n"
                else:
                    msg += " - Reason: None\n"
            except discord.NotFound:
                msg += f"- {action_type.capitalize()}: User ID {user_id} (Not Found)"  
                if reason:
                    msg += f" - Reason: {reason}\n"
                else:
                    msg += " - Reason: None\n" 
        await ctx.send(msg)
    else:
        await ctx.send("No recent moderation actions found.")
#clearmodlog for the sever owner of the sever
@bot.command() 
async def clearmodlog(self, ctx):
    if ctx.author.id == ctx.guild.owner_id:  # Check if command user is the server owner
        server_id = ctx.guild.id
        cursor.execute("DELETE FROM mod_actions WHERE server_id=?", (server_id,)) 
        conn.commit()
        await ctx.send("Moderation log cleared.")
    else:
        await ctx.send("You must be the server owner to use this command.")
# Remember to close the database connection when your bot shuts down
@bot.event
async def on_close():
    conn.close() 




























bot.run(token)
