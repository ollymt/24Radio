import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import os
import random
import asyncio
import json
from pathlib import Path
from mutagen import File
import tokens
from tokens import discord_token

from urllib.parse import quote_plus

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "music.json", "r") as f:
    music_data = json.load(f)

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='>', intents=intents, help_command=None)

chat_channel_id = 1193908637433876550
channel_id = 1312065642937188433

ad_folder = f"{BASE_DIR}/ad"
system_folder = f"{BASE_DIR}/system"

songs_between_ads = 5
current_song_count = 0
ads_enabled = True
connected = False
check_inactivity = True
inactivity_duration = 120
recent_songs = []  # store last few songs to avoid repeats

ad_table = [
    os.path.join(ad_folder, "spotify.mp3"),
    os.path.join(ad_folder, "je_katy.mp3"),
    os.path.join(ad_folder, "grubhub.mp3"),
    os.path.join(ad_folder, "je_latto.mp3"),
    os.path.join(ad_folder, "lim.mp3")
]

admins = [1197161924668952710]
admin_code = "t00fpAist"


async def get_song_duration(file_path):
    audio = File(file_path)
    if audio and audio.info and audio.info.length:
        return int(audio.info.length)
    return 180  # default 3 min if mutagen fails


@bot.event
async def on_ready():
    print("Bot is ready!")
    print("=============================")


@bot.event
async def on_voice_state_update(member, before, after):
    global connected, current_song_count
    if after.channel and after.channel.id == channel_id and (before.channel is None or before.channel.id != channel_id):
        if member.bot:
            return

        for vc in bot.voice_clients:
            if vc.channel.id == channel_id:
                return

        vc = await after.channel.connect()
        connected = True

        chat_channel = bot.get_channel(chat_channel_id)
        songs = list(music_data.keys())
        if not songs:
            print("No songs in music_data")
            return

        # play startup sound
        start_up = os.path.join(system_folder, "welcome.mp3")
        vc.play(FFmpegPCMAudio(start_up))
        await asyncio.sleep(40)

        while connected:
            if len(vc.channel.members) == 1:
                await vc.disconnect()
                connected = False
                break

            try:
                # pick a completely random song
                song_id = random.choice(list(music_data.keys()))
                current_song = music_data[song_id]

                song_path = str(BASE_DIR / current_song["path"])
                print(f"Playing song: {current_song['title']} by {current_song['artist']}")
                vc.play(FFmpegPCMAudio(song_path))

                lyric_term = f"{current_song['title']} by {current_song['artist']} lyrics"
                encoded = quote_plus(lyric_term)

                # send embed
                embed = discord.Embed(
                    title=f"{current_song['title']} - {current_song['artist']}",
                    description=f"Album: {current_song.get('album', '')}\n[View Lyrics](https://www.google.com/search?q={encoded})",
                    color=0x00b0f4
                )
                embed.set_author(name="🎶 Now Playing | 24Radio")
                if current_song.get("art"):
                    embed.set_image(url=current_song["art"])
                song_msg = await chat_channel.send(embed=embed)

                current_song_count += 1

                # play ad if needed
                if current_song_count >= songs_between_ads and ads_enabled:
                    ad_start = os.path.join(system_folder, "adbreak_start.mp3")
                    vc.play(FFmpegPCMAudio(ad_start))
                    await asyncio.sleep(40)

                    ad_path = random.choice(ad_table)
                    vc.play(FFmpegPCMAudio(ad_path))
                    await asyncio.sleep(await get_song_duration(ad_path) + 3)

                    ad_end = os.path.join(system_folder, "adbreak_end.mp3")
                    vc.play(FFmpegPCMAudio(ad_end))
                    await asyncio.sleep(30)

                    current_song_count = 0

                duration = await get_song_duration(song_path)
                await asyncio.sleep(duration + 3)

                try:
                    await song_msg.delete()
                    print("Deleted song info message")
                except Exception as e:
                    print(f"Could not delete message: {e}")

            except Exception as e:
                print(f"Error: {e}")
                error_path = os.path.join(system_folder, "error.mp3")
                vc.play(FFmpegPCMAudio(error_path))
                await asyncio.sleep(10)


@bot.command()
async def ping(ctx):
    latency = bot.latency * 1000
    await ctx.reply(f"Pong! 🏓 Latency: {latency:.2f} ms")

discord_token = os.getenv("DISCORD_TOKEN")

bot.run(discord_token)
