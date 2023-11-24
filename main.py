import os
import json
import random
import asyncio
import discord
from discord.ext import commands


'''
---------------- VARIABLES ----------------
'''
token = os.environ['TOKEN']
invite_url = os.environ['INVITE']
dir = './assets'
samples_dir = f'{dir}/samples'

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(
    description='Amen Break bot',
    intents=intents,
)


'''
---------------- CLASSES ----------------
'''


class User:
    def __init__(self, id: int, amen_id: str):
        self.id = id
        self.amen_id = amen_id

    def to_json(self):
        return {self.id, {"amen_id": self.amen_id}}


'''
---------------- FUNCTIONS ----------------
'''


def verify_data():
    try:
        with open('users.json', 'r') as file:
            json.load(file)
    except:
        print("User data file corrupted, generating new file")
        with open("users.json", "w") as file:
            json.dump({}, file)


# Get a random audio file from the samples directory and return its file name
def get_sample(index: int = None):
    if not index:
        index = random.randint(1, os.listdir(samples_dir).__len__() - 1)
    return os.listdir(samples_dir)[index]


# Get all copypasta records as a json file
def get_rants():
    with open(f'{dir}/copypastas.json', 'r') as file:
        return json.load(file)


# Get a discord user by its id and decode it into User object
def get_user(id):
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
            id_str = str(id)
            if users[id_str]:
                user = User(id, users[id_str].amen_id)
                print(f'User {id_str} found.')
                return user
    except:
        return None


# Insert or update user
def put_user(user: User):
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
            users[str(user.id)] = {"amen_id": user.amen_id}
    except:
        users = user.to_json()
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4, separators=(',', ': '))
        return True


'''
---------------- EVENTS ----------------
'''


@bot.event
async def on_ready():
    verify_data()
    print(f"{bot.user} (ID: {bot.user.id}) online!")
    print("-----------------------------------------------------")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="460 bpm breakcore/jungle/hardcore amen break"
    ))


# Read user's messages
@bot.event
async def on_message(message: discord.Message):
    # Ignore bot self messages
    if message.author.id == bot.user.id:
        return

    formatted_message = message.content.lower()

    # When a user's message contains the word "crazy"
    if formatted_message.__contains__("crazy"):
        await message.reply("Crazy? I was crazy once. They locked me in a room, a rubber room, a rubber room with "
                            "rats. And rats make me crazy. 🐀", mention_author=True)
    elif random.random() * 100 < 0.005:
        await message.reply("real", mention_author=True)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.respond(f"You're on cooldown ({round(error.retry_after, 2)})")


'''
---------------- COMMANDS ----------------
'''


async def vc_handler(ctx: discord.ApplicationContext, sample: str, status_message: str):
    vc = ctx.voice_client

    # Connect to voice chat
    if not vc:
        vc = await ctx.author.voice.channel.connect()
    # Check if the bot is not in the voice channel
    if ctx.author.voice.channel.id != vc.channel.id:
        return await ctx.respond(
            "You must be in the same voice channel as the bot.")
    if vc.is_playing():
        return await ctx.respond("Already amen breaking...")

    song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source=f'{sample}'), volume=0.75)

    if not song:  # check if the song is not found
        return await ctx.respond("There was an error.")  # return an error message
    else:
        await ctx.respond(status_message)  # return a message
        vc.play(song)  # play the song

    while vc.is_playing():  # Checks if voice is playing
        await asyncio.sleep(1)  # W hile it's playing it sleeps for 1 second
    else:
        await asyncio.sleep(1)  # If it's not playing it waits 15 seconds
        while vc.is_playing():  # and checks once again if the bot is not playing
            break  # if it's playing it breaks
        await vc.disconnect()  # if not it disconnects


def init_user(author: discord.User):
    user = get_user(author.id)
    if user is None:
        print(f"Registering user {author.id}.")
        random.seed(author.id)
        user = User(author.id, get_sample())
        put_user(user)
    return user


amen = discord.SlashCommandGroup("amen", "Do the amen and amen related activities")


@amen.command(description="Get a random break")
@commands.cooldown(1, 20, commands.BucketType.user)
async def post(ctx):
    sample = get_sample()
    print(f"User {ctx.author.id} requested sample {sample} ({type})")
    await ctx.respond(file=discord.File(f'{samples_dir}/{sample}'))


@amen.command(description="Play a random break on the voice chat")
@commands.cooldown(1, 3, commands.BucketType.guild)
async def play(ctx: discord.ApplicationContext):
    sample = get_sample()
    print(f"User {ctx.author.id} requested sample {sample} ({type})")
    await vc_handler(ctx, f'{samples_dir}/{sample}', f"Playing: `{sample}`")


@amen.command(description="Calculate the break meant for you")
@commands.cooldown(1, 20, commands.BucketType.user)
async def calculate(ctx, person: discord.Option(discord.SlashCommandOptionType.user, required=False,
                                                description="Check someone else's...")):
    user = init_user(person or ctx.author)
    return await ctx.respond((person.mention if person is not None else ctx.author.mention) + " amen break is...",
                             file=discord.File(f'{samples_dir}/{user.amen_id}'))


@amen.command(description="Learn the amen")
async def tabs(ctx):
    return await ctx.respond("```"
                             "Crash   |----------------|----------------|----------------|----------X-----|\n"
                             "Hi-hat  |x-x-x-x-x-x-x-x-|x-x-x-x-x-x-x-x-|x-x-x-x-x-x-x-x-|x-x-x-x-x---x-x-|\n"
                             "Snare   |----o--o-o--o--o|----o--o-o--o--o|----o--o-o----o-|-o--o--o-o----o-|\n"
                             "Kick    |o-o-------oo----|o-o-------oo----|o-o-------o-----|--oo------o-----|\n"
                             "        |1 + 2 + 3 + 4 + |1 + 2 + 3 + 4 + |1 + 2 + 3 + 4 + |1 + 2 + 3 + 4 + |"
                             "```")


bot.add_application_command(amen)


@bot.slash_command(name="poop", description="Play music that makes you poop 💩")
async def poop(
        ctx: discord.ApplicationContext,
        choice: discord.Option(
            str,
            choices=['play', 'stop'],
            required=True,
        )):
    vc = ctx.voice_client
    if choice == "play":
        await vc_handler(ctx, f'{dir}/poop.mp3', "Pooping :)")
    if choice == "stop":
        await vc.disconnect()
        await ctx.respond("Stopped pooping :(")


@bot.command(name="rant", description="Make it go schizo.")
async def rant(ctx):
    print(f"User {ctx.author.id} requested rant")
    rants = get_rants()
    await ctx.respond(rants[random.randint(0, len(rants) - 1)])


class EmbedActions(discord.ui.View):  # View that stores all embed's actions
    def __init__(self):
        super().__init__()
        button = discord.ui.Button(label="Invite", row=0, style=discord.ButtonStyle.url, url=invite_url)
        self.add_item(button)


@bot.command(name="about", description="About the bot.")
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title=bot.user.display_name,
        description="Bot that posts and plays random amen breaks.",
        color=discord.Colour.magenta(),
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1095774890579202050/1101090662331453501/icon.png")
    embed.add_field(name="Commands",
                    value="`/amen` - Do the amen and amen related activities.\n`/poop` - Start pooping \n`/rant` - Make it go schizo.\n")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1095774890579202050/1101090460635766784/thumbnail.png")
    embed.set_footer(text="made with 💊 by zoobdoob")

    await ctx.respond(embed=embed, view=EmbedActions())


'''
---------------- INIT ----------------
'''

bot.run(token)
