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

import mutagen
from mutagen import File

import tokens
from tokens import discord_token

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='>',intents=intents, help_command=None)

music_folder = r"/Users/justin/Documents/Documents - Justin's MacBook Pro/.just for fun/discordbots/24radio/music"
ad_folder = r"/Users/justin/Documents/Documents - Justin's MacBook Pro/.just for fun/discordbots/24radio/ad"

songs_between_ads = 5
current_song_count = 0
ads_enabled = True
queue = []
music_table = []

admins = [1197161924668952710]
admin_code = "t00fpAist"

channel_id = 1312065642937188433
connected = False
check_inactivity = True
inactivity_duration = 120

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

        while connected:
            if len(music_table) == 0:
                print("initializing queue")
                for song in songs:
                    music_table.append(song)

                print("shuffling queue")
                random.shuffle(music_table)

            global current_song_count
            print("checking if vc is still populated")
            if len(vc.channel.members) == 1:
                print("vc is not populated. disconnecting...")
                await vc.disconnect()
                connected = False
                break

            if len(music_table) > 0:
                if (current_song_count >= songs_between_ads) and (ads_enabled):
                    print("time for an ad!")
                    ad_path = os.path.join(ad_folder, "wanna_break_from_the_ads.mp3")
                    source = FFmpegPCMAudio(ad_path)
                    vc.play(source)
                    print("playing ad...")
                    await asyncio.sleep(33)
                    print("played ad")
                    current_song_count = 0
                
                current_song = os.path.join(music_folder, music_table[0])

                current_song_count += 1

                source = FFmpegPCMAudio(current_song)
                vc.play(source)
                print("playing song")
                await asyncio.sleep(await get_song_duration(current_song) + 3)
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

bot.run(tokens.discord_token)