import discord
from discord.ext import commands
import os 
from keep_alive import keep_alive
keep_alive()
import random

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
    await bot.change_presence(activity=discord.Game(name="with your heart"))
  


@bot.command(pass_context=True)
async def botcommands(ctx, *, command=None):
    """Display help information."""
    if command is None:
        embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
        for command in bot.commands:
            embed.add_field(name=command.name, value=command.help, inline=False)
        await ctx.send(embed=embed)
    else:
        cmd = bot.get_command(command)
        if cmd:
            embed = discord.Embed(title=f"Help for {cmd.name}", description=cmd.help, color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            await ctx.send("Command not found.")

#ping command
@bot.command(name='ping', help='Check bot latency')
async def ping_command(ctx):
    latency = bot.latency
    await ctx.send(f'Pong! Latency: **{round(latency * 1000)}**ms')

@bot.command(name='kick', help='Kick a member.')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    """Kick a member."""
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked. Reason: {reason}")

@bot.command(name='ban', help='Ban a member.')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    """Ban a member."""
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned. Reason: {reason}")

@bot.command(name='unban', help='Unban a member.')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    """Unban a member."""
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} has been unbanned.")
            return

@bot.command(name='mute', help='Mute a member.')
async def mute(ctx, member: discord.Member, duration: int = None):
    """Mute a member."""
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)

    await member.add_roles(muted_role)
    await ctx.send(f"{member.mention} has been muted.")

    if duration:
        await asyncio.sleep(duration * 60)
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} has been unmuted after {duration} minutes.")

@bot.command(name='warn', help='Warn a member.')
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    """Warn a member."""
    # You can implement your warning logic here
    await ctx.send(f"{member.mention} has been warned. Reason: {reason}")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to mute members.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please mention a valid member to mute.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid arguments provided.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        await ctx.send("An error occurred while processing the command.")

@bot.command(name='clear', help='Clear a specified number of messages.')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Clear a specified number of messages."""
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Cleared {amount} messages.")  


@bot.command(name='hello', help='Say hello to the bot.')
async def hello(ctx):
    """Say hello to the bot."""
    await ctx.send(f'Hello {ctx.author.mention}!')

@bot.command(name='coinflip', help='Flip a coin.')
async def coinflip(ctx):
    """Flip a coin."""
    result = 'Heads' if random.randint(0, 1) == 0 else 'Tails'
    await ctx.send(f"The coin landed on: {result}")

@bot.command(name='roll', help='Roll a dice.')
async def roll(ctx, sides: int = 6):
    """Roll a dice."""
    if sides < 2:
        await ctx.send("Dice must have at least 2 sides.")
        return

    result = random.randint(1, sides)
    await ctx.send(f"You rolled a {sides}-sided dice and got: {result}")

@bot.command(name='echo', help='Echo back your message.')
async def echo(ctx, *, message):
    """Echo back your message."""
    await ctx.send(message)

@bot.command(name='avatar', help='Get the avatar of a user.')
async def avatar(ctx, member: discord.Member = None):
    """Get the avatar of a user."""
    member = member or ctx.author
    await ctx.send(member.avatar_url)

bot.command(name='8ball', help='Ask the magic 8-ball a question.')
async def eight_ball(ctx, *, question):
    """Ask the magic 8-ball a question."""
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.",
        "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."
    ]
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@bot.command(name='choose', help='Let the bot choose between multiple options.')
async def choose(ctx, *options):
    """Let the bot choose between multiple options."""
    if len(options) < 2:
        await ctx.send("Please provide at least 2 options.")
        return
    await ctx.send(f"I choose: {random.choice(options)}")

@bot.command(name='roll_dice', help='Roll multiple dice with specified sides.')
async def roll_dice(ctx, num_dice: int = 1, sides: int = 6):
    """Roll multiple dice with specified sides."""
    if num_dice < 1:
        await ctx.send("Please specify at least 1 die to roll.")
        return
    if sides < 2:
        await ctx.send("Dice must have at least 2 sides.")
        return

    rolls = [random.randint(1, sides) for _ in range(num_dice)]
    await ctx.send(f"You rolled {num_dice} {sides}-sided dice and got: {', '.join(map(str, rolls))}")

@bot.command(name='rps', help='Play rock-paper-scissors with the bot.')
async def rps(ctx, choice: str):
    """Play rock-paper-scissors with the bot."""
    choices = ["rock", "paper", "scissors"]
    if choice.lower() not in choices:
        await ctx.send("Invalid choice. Please choose rock, paper, or scissors.")
        return

    bot_choice = random.choice(choices)
    if choice.lower() == bot_choice:
        await ctx.send(f"It's a tie! Both chose {choice}")
    elif (choice.lower() == "rock" and bot_choice == "scissors") or \
         (choice.lower() == "paper" and bot_choice == "rock") or \
         (choice.lower() == "scissors" and bot_choice == "paper"):
        await ctx.send(f"You win! {choice.capitalize()} beats {bot_choice}")
    else:
        await ctx.send(f"You lose! {bot_choice.capitalize()} beats {choice}")

@bot.command(name='quote', help='Get a random famous quote.')
async def quote(ctx):
    """Get a random famous quote."""
    quotes = [
        "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "Your time is limited, so don't waste it living someone else's life. - Steve Jobs",
        "If life were predictable it would cease to be life, and be without flavor. - Eleanor Roosevelt",
        "Life is what happens when you're busy making other plans. - John Lennon",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt"
    ]
    await ctx.send(random.choice(quotes))

@bot.command(name='fact', help='Get a random interesting fact.')
async def fact(ctx):
    """Get a random interesting fact."""
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
        "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
        "A day on Venus is longer than a year on Venus. Venus takes about 243 Earth days to rotate on its axis, but only about 225 Earth days to orbit the Sun.",
        "Octopuses have three hearts. Two pump blood to the gills, while the third pumps it to the rest of the body.",
        "Bananas are berries, but strawberries are not. In botanical terms, a berry is a fruit produced from the ovary of a single flower with seeds embedded in the flesh.",
        "The world's largest snowflake was 15 inches wide and 8 inches thick. It was recorded in Montana in 1887."
    ]
    await ctx.send(random.choice(facts))


@bot.command(name='compliment', help='Get a random compliment.')
async def compliment(ctx):
    """Get a random compliment."""
    compliments = [
        "You're an awesome friend!", "You have a great sense of humor.", "You're a wonderful person.", "You're always so helpful.", "You're incredibly talented.",
        "You make a positive impact on everyone you meet.", "You're a true inspiration.", "You have a heart of gold.", "You're doing a fantastic job!", "You're beautiful inside and out."
    ]
    await ctx.send(random.choice(compliments))

@bot.command(name='roast', help='Get a random roast.')
async def roast(ctx):
    """Get a random roast."""
    roasts = [
        "If brains were dynamite, you wouldn't have enough to blow your nose.", "If you were twice as smart, you'd still be half as smart as you think you are.",
        "I'd agree with you, but then we'd both be wrong.", "I'm jealous of all the people who haven't met you.", "You bring everyone so much joy... when you leave the room.",
        "I'd tell you to go to hell, but I work there and I don't want to see you every day.", "You're not pretty enough to be this stupid.", "You're about as useful as a screen door on a submarine.",
        "I'd insult you more, but Mother Nature did such a good job already.", "I've seen people like you before, but I had to pay admission."
    ]
    await ctx.send(random.choice(roasts))

@bot.command(name='insult', help='Get a random insult.')
async def insult(ctx):
    """Get a random insult."""
    insults = [
        "Were you born on the highway? Because that's where most accidents happen.", "You're not funny, but your life, now that's a joke!", 
        "You must have been born on a highway because that's where most accidents happen.", "Is your name Google? Because you have everything I've been searching for... in my nightmares!",
        "If laughter is the best medicine, your face must be curing the world!", "Your face makes onions cry.", 
        "You're the reason the gene pool needs a lifeguard.", "I'd explain it to you, but I don't have any crayons.", 
        "You must have a low opinion of people if you think they're your friends.", "Your family tree must be a cactus because everybody on it is a prick."
    ]
    await ctx.send(random.choice(insults))

#gayrate
@bot.command(name='gayrate', help='Check the gayness of a user.')
async def gayrate(ctx, member: discord.Member = None):
    """Check the gayness of a user."""
    if member is None:
        member = ctx.author

    gayness_percentage = random.randint(0, 100)
    await ctx.send(f"{member.mention} is {gayness_percentage}% gay.")

#simprate
@bot.command(name='simprate', help='Check the simpness of a user.')  
async def simprate(ctx, member: discord.Member = None):
    """Check the simpness of a user."""
    if member is None:
        member = ctx.author

    simpness_percentage = random.randint(0, 100)
    await ctx.send(f"{member.mention} is {simpness_percentage}% simp.")

#pprate
@bot.command(name='pprate', help='Check the size of a user\'s pp.')
async def pprate(ctx, member: discord.Member = None):
    """Check the size of a user's pp."""
    if member is None:
        member = ctx.author

    pp_size = random.randint(0, 20)
    pp_string = "8" + "=".repeat(pp_size) + "D"
    await ctx.send(f"{member.mention}'s pp size is {pp_string}")

#dackrate
@bot.command(name='dackrate', help='Check the dick size of a user.')
async def dackrate(ctx, member: discord.Member = None):
    """Check the dick size of a user."""
    if member is None:
        member = ctx.author

    dick_size = random.randint(0, 20)
    dick_string = "8" + "=".repeat(dick_size) + "D"
    await ctx.send(f"{member.mention}'s dick size is {dick_string}")

@bot.command(name='guess', help='Guess the number between 1 and 100.')
async def guess(ctx, number: int):
    """Guess the number between 1 and 100."""
    actual_number = random.randint(1, 100)
    if number == actual_number:
        await ctx.send(f"Congratulations! You guessed the correct number: {actual_number}")
    else:
        await ctx.send(f"Sorry, the correct number was: {actual_number}")

@bot.command(name='rpsls', help='Play Rock-Paper-Scissors-Lizard-Spock.')
async def rpsls(ctx, choice: str):
    """Play Rock-Paper-Scissors-Lizard-Spock."""
    choices = ['rock', 'paper', 'scissors', 'lizard', 'spock']
    if choice.lower() not in choices:
        await ctx.send("Invalid choice. Please choose rock, paper, scissors, lizard, or spock.")
        return

    bot_choice = random.choice(choices)
    if choice.lower() == bot_choice:
        await ctx.send(f"It's a tie! Both chose {choice}")
    elif (choice.lower() == 'rock' and bot_choice in ['scissors', 'lizard']) or \
         (choice.lower() == 'paper' and bot_choice in ['rock', 'spock']) or \
         (choice.lower() == 'scissors' and bot_choice in ['paper', 'lizard']) or \
         (choice.lower() == 'lizard' and bot_choice in ['spock', 'paper']) or \
         (choice.lower() == 'spock' and bot_choice in ['scissors', 'rock']):
        await ctx.send(f"You win! {choice.capitalize()} beats {bot_choice}")
    else:
        await ctx.send(f"You lose! {bot_choice.capitalize()} beats {choice}")

@bot.command(name='hangman', help='Play Hangman game.')
async def hangman(ctx):
    """Play Hangman game."""
    word_list = ['python', 'java', 'javascript', 'ruby', 'swift', 'kotlin', 'csharp', 'html', 'css']
    word = random.choice(word_list)
    guessed_letters = []
    attempts = 6
    hidden_word = ['_'] * len(word)

    async def update_hidden_word():
        return ' '.join(hidden_word)

    async def check_guess(letter):
        nonlocal attempts
        if letter in guessed_letters:
            return await ctx.send("You've already guessed that letter.")
        guessed_letters.append(letter)
        if letter not in word:
            attempts -= 1
            if attempts == 0:
                await ctx.send(f"You're out of attempts! The word was: {word}")
                return True
            else:
                await ctx.send(f"Incorrect guess! You have {attempts} attempts left.")
        else:
            for i, char in enumerate(word):
                if char == letter:
                    hidden_word[i] = letter
            if '_' not in hidden_word:
                await ctx.send(f"Congratulations! You guessed the word: {''.join(hidden_word)}")
                return True
            else:
                await ctx.send(f"Correct guess! {' '.join(hidden_word)}")
        return False

    await ctx.send(f"Let's play Hangman! The word has {len(word)} letters.")
    await ctx.send(await update_hidden_word())

    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author

    while True:
        try:
            message = await bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Time's up! You took too long to guess.")
            break
        if len(message.content) != 1 or not message.content.isalpha():
            await ctx.send("Please enter a single letter.")
            continue
        if await check_guess(message.content.lower()):
            break



bot.run(token)
  
  





