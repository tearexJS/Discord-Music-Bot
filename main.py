
import discord
import os
import asyncio
from discord import voice_client
# load our local env so we dont have the token in public
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from youtube_dl import YoutubeDL
import validators

load_dotenv()
client = commands.Bot(command_prefix='.')  # prefix our commands with '.'

players = {}
q = []
"""
def play_next(ctx, source):
    if len() >= 1:
        del q[0]
        voice = get(client.voice_clients, guild=ctx.guild)
        voice.play(discord.FFmpegPCMAudio(source=source, after=lambda e: play_next(ctx)))
        asyncio.run_coroutine_threadsafe(ctx.send("No more songs in q."))
"""
#def remFromQ(number):

def is_connected(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

def is_playing(ctx):
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client.is_playing()

def addToQ(url):
    q.append(url)

def checkQ(ctx, voice):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if not is_playing(ctx) and q:
        url = q[0]
        q.pop(0)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after = lambda e: checkQ(ctx, voice))

        
    else:
        #ctx.send('Q
        # is empty. FEED ME WITH MOAR MUSIC :slight_smile:')
        return
    
@client.event  # check if bot is ready
async def on_ready():
    print('Bot online')


# command for bot to join the channel of the user, if the bot has already joined and is in a different channel, it will move to the channel the user is in
@client.command(pass_context=True)
async def join(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
    else:
        await ctx.send('YO NOT CONNECTED')

# command to play sound from a youtube URL

@client.command()
async def play(ctx, url):
    YDL_OPTIONS = {'format': 'bestaudio'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    if not validators.url(url):
        await ctx.send('Not a valid URL')
    os.system('youtube-dl -j --flat-playlist '+url)
    if not is_connected(ctx):
        await ctx.send(':slight_smile:')
        await join(ctx)
    voice = get(client.voice_clients, guild=ctx.guild)
    print(url)
    if not is_playing(ctx):
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        
    voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after = lambda e: checkQ(ctx, voice))
    voice.is_playing()
    await ctx.send('Bot is playing')
# check if the bot is already playing
    else:
        addToQ(url)
        print(type(q), type(ctx))
        print(q)



@client.command()
async def queue(ctx):
    await ctx.send('Current queue: ')
    await ctx.send(q)



# command to resume voice if it is paused
@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming')


# command to pause voice if it is playing
@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')


# command to stop voice
@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')


# command to clear channel messages
@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    await ctx.send("Messages have been cleared")

@client.command()
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect() # Leave the channel
        await ctx.send('Idzem')
    else:
        await ctx.send('Fok of i ain\'t connected :slight_smile:')


client.run(os.getenv('TOKEN'))