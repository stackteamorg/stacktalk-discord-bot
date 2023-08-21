#!/usr/bin/env python

import asyncio
import datetime
import discord
import discord.ext.commands
import queue as Queue

import captcha
import youtube


discord_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
description = 'Discord bot'

music_queue = Queue.Queue()
current_music = None

intents = discord.Intents.default()
intents.bans = True
intents.members = True
intents.message_content = True
intents.moderation = True
intents.voice_states = True

bot = discord.ext.commands.Bot(command_prefix='!',
                               description=description,
                               intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')


@bot.command()
async def help_me(ctx):
    help_message = '''
    Available commands:
    !help           Shows this message
    !pause          This command pauses the song
    !play           Play a music by its name from YouTube
    !resume         Resumes
    !stop           Stop
    !queue          Show the music queue
    !reset          Reset the music queue
    '''
    await ctx.send(help_message)


@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()

    else:
        await ctx.send("I'm not playing anything right now.")


def play_handler(ctx, current_music, retry):
    def x(e):
        if e is not None and retry:
            music_queue.queue = Queue.deque([current_music] + list(music_queue.queue))

        asyncio.run_coroutine_threadsafe(skip(ctx, False), bot.loop)

    return x


@bot.command()
async def skip(ctx, retry=True):
    global current_music
    voice_client = ctx.voice_client
    if voice_client is not None:
        voice_client.stop()
        if not music_queue.empty():
            current_music = music_queue.get()
            voice_client.play(discord.FFmpegPCMAudio(current_music[1],
                                                     before_options='-reconnect 1 -reconnect_at_eof 0 -reconnect_streamed 1 -reconnect_delay_max 10',
                                                     options='-vn'),
                              after=play_handler(ctx, current_music, retry))
            await ctx.send(f'Playing "{current_music[0]}"')

        else:
            await voice_client.disconnect()
            current_music = None

    else:
        await ctx.send("I can't skip.")


@bot.command()
async def play(ctx, *, query=None):
    global current_music
    if query is None:
        await ctx.send('Please provide a query to search for on YouTube. Usage: !play <query>')
        return

    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if voice_client:
        await voice_client.move_to(voice_channel)

    else:
        voice_client = await voice_channel.connect()

    try:
        music = await youtube.yt_audio_search(query)
        music_queue.put(await youtube.yt_audio_search(query))
        if not voice_client.is_playing():
            voice_client.stop()
            current_music = music_queue.get()
            voice_client.play(discord.FFmpegPCMAudio(current_music[1],
                                                     before_options='-reconnect 1 -reconnect_at_eof 0 -reconnect_streamed 1 -reconnect_delay_max 10',
                                                     options='-vn'),
                              after=play_handler(ctx, current_music, True))
            await ctx.send(f'Playing "{current_music[0]}"')
        else:
            await ctx.send(f'"{music[0]}" added to the queue, you can skip to the next song by !skip')

    except Exception as e:
            await ctx.send(f'Error: {str(e)}')


@bot.command()
async def resume(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send(f'Playing "{current_music[0]}"')

    else:
        await ctx.send("I'm not paused right now.")


@bot.command()
async def stop(ctx):
    global current_music
    voice_client = ctx.voice_client
    if voice_client:
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
            await voice_client.disconnect()
            current_music = None

        else:
            await ctx.send("I'm not playing anything right now.")

    else:
        await ctx.send("I'm not in a voice channel.")


@bot.command()
async def queue(ctx):
    cm_msg = 'Current song: None' if current_music is None else f'Current song: "{current_music[0]}"'
    if music_queue.empty():
        await ctx.send(cm_msg + '\n\nThe queue is empty')

    else:
        msg = ''
        for id, obj in enumerate(music_queue.queue, 1):
            msg += f'{id}. {obj[0]}\n'

        await ctx.send(cm_msg + '\n\n' + msg)
        

@bot.command()
async def reset(ctx):
    while not music_queue.empty():
        music_queue.get()


@play.error
async def play_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send('Please provide a query to search for on YouTube. Usage: !play <query>')


@bot.event
async def on_member_join(ctx):
    def check(m):
        return m.author.id == ctx.id and bool(m.content)

    await ctx.timeout(datetime.timedelta(minutes=1))
    cap = await captcha.generate_captcha()

    await ctx.send(f'Welcome {ctx.name}!\nPlease solve the captcha')
    await ctx.send(f'What is the result of the following statement?\n{cap[0]}\n\n'
                      'You only have one chance to answer, please be careful.')

    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
        if msg.content == cap[1]:
            await ctx.send('Thank you, enjoy the server.')
            await ctx.timeout(datetime.timedelta())
        else:
            raise asyncio.TimeoutError()

    except asyncio.TimeoutError:
        await ctx.send("You didn't solve the captcha, so we decided to kick you.")
        await ctx.kick()


bot.run(discord_token)
