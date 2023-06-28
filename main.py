import dotenv
import os
import discord
from datetime import datetime
import json
import random
import asyncio

'''
---------------- VARIABLES ----------------
'''
dotenv.load_dotenv()
token = os.getenv("TOKEN")
invite_url = os.getenv("INVITE")
dir = './assets'
samples_dir = f'{dir}/samples'

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(
    description='Amen Break bot',
    intents=intents,
)

crazy_text = "Crazy? I was crazy once. They locked me in a room, a rubber room, a rubber room with rats. And rats make me crazy. 🐀"

'''
---------------- CLASSES ----------------
'''


class Server:
    def __init__(self, id: str, crazy_event: bool):
        self.id = id
        self.crazy_event = bool

    def to_json(self):
        return {self.id, self.crazy_event}


class User:
    def __init__(self, id: str, timestamp: datetime):
        self.id = id
        self.timestamp = timestamp

    def to_json(self):
        return {self.id, self.timestamp.isoformat()}


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
def get_sample():
    count = 0
    for path in os.scandir(samples_dir):
        if path.is_file():
            count += 1
    index = random.randint(0, count - 1)
    file = os.listdir(samples_dir)[index]
    return file


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
                user = User(id_str, datetime.strptime(users[id_str], '%Y-%m-%dT%H:%M:%S.%f'))
                print(f'User {id_str} found.')
                return user
    except:
        return None


# Insert or update user
def put_user(user: User):
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
            users[user.id] = user.timestamp.isoformat()
    except:
        users = user.to_json()
    with open("users.json", "w") as file:
        json.dump(users, file)
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


# When a user's message contains the word "crazy"
@bot.event
async def on_message(message: discord.Message):
    # Make sure we won't be replying to ourselves.
    if message.author.id == bot.user.id:
        return

    if message.content.__contains__("crazy"):
        await message.reply(crazy_text, mention_author=True)


'''
---------------- COMMANDS ----------------
'''


# TODO fix exploit where using post resets play cooldown
@bot.command(name="amen", description="Get a random amen break sample.")
async def amen(
        ctx: discord.ApplicationContext,
        type: discord.Option(
            str,
            choices=['post', 'play'],
            required=False,
            default="post",
            description="Choose between posting a sample or playing on a voice channel."
        )
):
    user = get_user(ctx.author.id)
    if user == None:
        print(f"Registering user {ctx.author.id}.")
        user = User(ctx.author.id, datetime.now())

    if type == "post":
        cooldown = 5
    else:
        cooldown = 180
    time_diff = datetime.now() - user.timestamp
    if time_diff.seconds == 0 or time_diff.seconds >= cooldown:
        sample = get_sample()
        print(f"User {ctx.author.id} requested sample {sample} ({type})")
        if type == "post":
            await ctx.respond(file=discord.File(f'{samples_dir}/{sample}'))
        else:
            vc = ctx.voice_client  # define our voice client

            if not vc:  # check if the bot is not in a voice channel
                vc = await ctx.author.voice.channel.connect()  # connect to the voice channel
            if ctx.author.voice.channel.id != vc.channel.id:  # check if the bot is not in the voice channel
                return await ctx.respond("You must be in the same voice channel as the bot.")  # return an error message
            if vc.is_playing():
                return await ctx.respond("Bot already playing.")  # return an error message

            song = discord.PCMVolumeTransformer(
                # discord.FFmpegPCMAudio(executable=f'{ffmpeg_dir}', source=f'{samples_dir}/{sample}'), volume=0.75)
                discord.FFmpegPCMAudio(source=f'{samples_dir}/{sample}'), volume=0.75)

            if not song:  # check if the song is not found
                return await ctx.respond("There was an error.")  # return an error message
            else:
                await ctx.respond(f"Playing: `{sample}`")  # return a message
                vc.play(song)  # play the song

            while vc.is_playing():  # Checks if voice is playing
                await asyncio.sleep(1)  # W hile it's playing it sleeps for 1 second
            else:
                await asyncio.sleep(1)  # If it's not playing it waits 15 seconds
                while vc.is_playing():  # and checks once again if the bot is not playing
                    break  # if it's playing it breaks
                await vc.disconnect()  # if not it disconnects
        user.timestamp = datetime.now()
        put_user(user)
    else:
        print(f"User {ctx.author.id} request denied (Cooldown)")
        return await ctx.respond(
            f"You're on cooldown ({cooldown - time_diff.seconds} seconds left)")  # return an error message


@bot.command(name="rant", description="Make it go schizo.")
async def rant(ctx):
    print(f"User {ctx.author.id} requested rant")
    rants = get_rants()
    await ctx.respond(rants[random.randint(0, len(rants) - 1)])


@bot.command(name="crazy", description="I was crazy once...")
async def rant(ctx):
    await ctx.respond(crazy_text)


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
    embed.add_field(name="Commands", value="`/amen` - Get a random amen break sample.\n`/rant` - Make it go schizo.\n`/crazy` - I was crazy once...")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1095774890579202050/1101090460635766784/thumbnail.png")
    embed.set_footer(text="made with 💊 by zoobdoob")

    await ctx.respond(embed=embed, view=EmbedActions())


'''
---------------- INIT ----------------
'''
bot.run(token)
