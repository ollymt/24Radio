import discord
from discord.ext import commands
from discord.ext.commands import bot
from discord import FFmpegPCMAudio

import ffmpeg
import os
from os import path
from os import listdir
import random
import asyncio
import json
import time

import mutagen
from mutagen import File

import tokens
from tokens import discord_token

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='>',intents=intents, help_command=None)

root = r"/Users/justin/Documents/Documents - Justin's MacBook Pro/.just for fun/discordbots/24radio"
music_folder = os.path.join(root, "music")
ad_folder = os.path.join(root, "ad")
system_folder = os.path.join(root, "system")
requests_json = os.path.join(root, "requests.json")
last_request_json = os.path.join(root, "last_requests.json")

songs_between_ads = 5
current_song_count = 0
request_cooldown = 3600 # in seconds
ads_enabled = True
queue = {}
music_table = {}
ad_table = {
    os.path.join(ad_folder, "spotify.mp3"),
    os.path.join(ad_folder, "je_katy.mp3"),
    os.path.join(ad_folder, "grubhub.mp3"),
    os.path.join(ad_folder, "je_latto.mp3"),
    os.path.join(ad_folder, "lim.mp3")
}
song_requests = {}
last_requests = {}

admins = [1197161924668952710]
admin_code = "t00fpAist"

channel_id = 1312065642937188433
connected = False
check_inactivity = True
inactivity_duration = 120

async def play_song(vc, file_path):
    """
    Plays a song and waits for it to finish before returning.
    """
    source = FFmpegPCMAudio(file_path)
    vc.play(source)

    # Wait until the song finishes playing
    while vc.is_playing():
        await asyncio.sleep(1)  # Check every 1 second if the audio is still playing


async def get_song_duration(file_path):
    # Load the audio file
    audio = File(file_path)
    
    # Check if the file was loaded successfully and has a duration
    if audio and audio.info and audio.info.length:
        return int(audio.info.length)  # Duration in seconds
    else:
        return None  # Couldn't retrieve duration

async def monitor_inactivity(vc):
    while check_inactivity:
        await asyncio.sleep(inactivity_duration)

        if len(vc.channel.members) == 1:
            await vc.disconnect()
            connected = False
            break


@bot.event
async def on_ready():
    global song_requests
    global last_requests

    print("loading song requests...")
    try:
        with open(requests_json, "r") as file:
            song_requests = json.load(file)
    except FileNotFoundError:
        song_requests = {}

    print("loading last requests...")
    try:
        with open(last_request_json, "r") as file:
            last_requests = json.load(file)
    except FileNotFoundError:
        last_requests = {}

    print("bot is ready!")
    print("=============================")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == channel_id and (before.channel is None or before.channel.id is not channel_id):
        voice_channel = after.channel

        if member.bot:
            return
        
        for vc in bot.voice_clients:
            if vc.channel.id == channel_id:
                return

        vc = await voice_channel.connect()
        global connected
        connected = True

        songs = os.listdir(music_folder)
        if not songs:
            print("no songs in folder")
            return
        
        start_up = os.path.join(system_folder, "welcome.mp3")
        startupSource = FFmpegPCMAudio(start_up)
        vc.play(startupSource)
        await asyncio.sleep(40)

        while connected:
            if len(music_table) == 0:
                print("initializing queue")
                for song in songs:
                    music_table.append(song)
                random.shuffle(music_table)

            global current_song_count
            print("checking if vc is still populated")
            if len(vc.channel.members) == 1:
                print("vc is not populated. disconnecting...")
                await vc.disconnect()
                connected = False
                break

            if len(music_table) > 0:
                if (current_song_count >= songs_between_ads) and ads_enabled:
                    print("time for an ad!")
                    ad_announcement = os.path.join(system_folder, "adbreak_start.mp3")
                    await play_song(vc, ad_announcement)

                    ad_path = random.choice(ad_table)
                    print("playing ad...")
                    await play_song(vc, ad_path)

                    current_song_count = 0
                    ad_announcement_end = os.path.join(system_folder, "adbreak_end.mp3")
                    await play_song(vc, ad_announcement_end)
                    continue

                try:
                    current_song = os.path.join(music_folder, music_table[0])
                    current_song_count += 1

                    print(f"playing song: {current_song}")
                    await play_song(vc, current_song)

                except Exception as e:
                    print(f"An error occurred while playing the song: {e}")
                    error_audio = os.path.join(system_folder, "error.mp3")
                    await play_song(vc, error_audio)

                music_table.pop(0)
                print("played song")


@bot.command()
async def help(ctx, arg=None):
    embed = discord.Embed(title="Help Menu",
                      description="**How to use 24Radio?**\nSimply join the 24radio voice channel and 24Radio would automatically play unlimited music for you!\n\n**DISCLAIMER:** 24Radio is intended to be solely used privately on the Yogamat server. No copyright infringement intended.\n\n**Songs Included:** (List is not final and may be increased or decreased.)",
                      colour=0xff9300)

    embed.set_author(name="24Radio")

    embed.add_field(name="- C418",
                    value="- - Subwoofer Lullaby\n- - Moog City\n- - Minecraft\n- - Mice on Venus\n- - Dry Hands\n- - Wet Hands\n- - Sweden\n- - Cat\n- - Moog City 2",
                    inline=True)
    embed.add_field(name="- Lena Raine",
                    value="- - Pigstep",
                    inline=True)
    embed.add_field(name="- LSPLASH",
                    value="- - Dawn of the Doors\n- - Elevator Jam\n- - Guiding Light",
                    inline=True)
    embed.add_field(name="- Tobu",
                    value="- - Cruel\n- - Cacao\n- - Candyland",
                    inline=True)
    embed.add_field(name="- Dimrain47",
                    value="- - At the Speed of Light",
                    inline=True)
    embed.add_field(name="- djNate",
                    value="- - Theory of Everything",
                    inline=True)
    embed.add_field(name="- F777",
                    value="- - Deadlocked",
                    inline=True)
    embed.add_field(name="- DrPhonics",
                    value="- - Code Red",
                    inline=True)
    embed.add_field(name="- Forever Bound",
                    value="- - Stereo Madness",
                    inline=True)
    embed.add_field(name="- Nintendo",
                    value="- - Wii Shop Channel Main Theme\n- - Wii Sports Title Theme\n- - Mii Channel Main Theme\n- - Earthbound Sanctuary Guardians",
                    inline=True)
    embed.add_field(name="- Joo Won",
                    value="- - Fly Me to the Moon (Squid Game OST)",
                    inline=True)
    embed.add_field(name="- The Caretaker",
                    value="- - It's just a burning memory",
                    inline=True)
    embed.add_field(name="- Jschlatt",
                    value="- - Santa Claus Is Coming To Town",
                    inline=True)
    embed.add_field(name="- Noisestorm",
                    value="- - Crab Rave",
                    inline=True)
    embed.add_field(name="- NOMA",
                    value="- - Brain Power",
                    inline=True)
    embed.add_field(name="- JT Music",
                    value="- - Join Us For A Bite",
                    inline=True)
    embed.add_field(name="- The 8-Bit Big Band",
                    value="- - Five Nights At Freddy's (Big Band Version)\n- - It's Been So Long (Big Band Version)",
                    inline=True)
    embed.add_field(name="- AJR",
                    value="- - Touchy Feely Fool\n- - 100 Bad Days\n- - The Dumb Song\n- - Burn The House Down\n- - Karma (Live from OSN)\n- - Way Less Sad\n- - Sober Up (feat. Rivers Cuomo)\n- - Weak\n- - Alice By The Hudson\n- - Pitchfork Kids\n- - Growing Old On Bleecker Street",
                    inline=True)
    embed.add_field(name="- Anuc Atittawan",
                    value="- - The Christmas Song\n- - The Christmas Song (feat. 13336hera)\n- - Santa Claus is Coming to Town (feat. 13336hera)\n- - All I Want For Christmas is You (feat. 13336hera)\n- - Let It Snow (feat. 13336hera)",
                    inline=True)

    
    await ctx.reply(embed=embed)

@bot.command()
async def adfrequency(ctx, count):
    if ctx.author.id in admins:
        global songs_between_ads
        global ads_enabled

        if isinstance(int(count), int) and int(count) > 0:
            songs_between_ads = int(count)
            ads_enabled = True
            await ctx.reply(f"Ads will now play after {count} songs.")
        else:
            await ctx.reply("Invalid parameters")
    else:
        await ctx.reply("You do not have permissions to use this command.")

@bot.command()
async def adsenabled(ctx, value):
    if ctx.author.id in admins:
        global ads_enabled

        if value == "true":
            ads_enabled = True
            await ctx.reply("Ads enabled")
        elif value == "false":
            ads_enabled = False
            await ctx.reply("Ads disabled")
        else:
            await ctx.reply("Invalid parameters")
    else:
        await ctx.reply("You do not have permissions to use this command.")

@bot.command()
async def reset(ctx, code):
    if ctx.author.id in admins:
        global ads_enabled
        global songs_between_ads
        global admin_code

        if code == admin_code:
            ads_enabled = True
            songs_between_ads = 5
            await ctx.reply("Bot settings has been reset")
        else:
            await ctx.reply("Incorrect code")
    else:
        await ctx.reply("You do not have permissions to use this command.")

@bot.command()
async def ping(ctx):
    """
    Returns the bot's ping in milliseconds.
    """
    latency = bot.latency * 1000  # Convert from seconds to milliseconds
    await ctx.reply(f"Pong! 🏓 Latency: {latency:.2f} ms")

async def add_request(username, link, status="pending"):
    global song_requests
    request_exists = False
    can_request = True

    # Check if the user is in cooldown
    if username in last_requests and time.time() - last_requests[username] < request_cooldown:
        return f"Wait {int((request_cooldown - (time.time() - last_requests[username])) / 60)} minutes before requesting again!"

    # Check if the song was already requested
    for request in song_requests:
        if request["link"] == link:
            request_exists = True
            request["request_index"] += 1
            break  # No need to keep looping after finding the song

    # Add new request if it doesn't exist
    if not request_exists:
        song_requests[len(song_requests)] = {
            "username": username,
            "link": link,
            "request_index": 1,
            "status": "pending",
            "timestamp": time.time()
        }

    # Update last request time
    last_requests[username] = time.time()

    print("saving request...")
    saved = await save_request()
    if not saved:
        return "Your request was not saved! Try again later"
    
    return "✅ Your request has been added!"

async def save_request():
    success = True
    try:
        print("writing requests.json...")
        with open(requests_json, "w") as file:
            json.dump(song_requests, file, indent=4)
        print("success writing requests.json")
    except Exception as e:
        print(f"error: {e}")
        success = False
    
    try:
        print("writing last_requests.json...")
        with open(last_request_json, "w") as file:
            json.dump(last_requests, file, indent=4)
        print("success writing last_requests.json")
    except Exception as e:
        print(f"error: {e}")
        success = False

    return success

        

@bot.command()
async def request(ctx, link):
    link = str(link)
    user = ctx.author
    if "https://www.youtube.com/watch" in link or "https://youtu.be/" in link:
        await ctx.reply(await add_request(user.name, link))
    else:
        await ctx.reply("Must be a YouTube link!")

bot.run(tokens.discord_token)
