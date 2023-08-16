#!/usr/bin/env python

import asyncio
import captcha
import datetime
import discord
import discord.ext.commands
import os

description = "Captcha bot"

intents = discord.Intents.default()
intents.bans = True
intents.members = True
intents.message_content = True
intents.moderation = True

bot = discord.ext.commands.Bot(command_prefix='!',
                               description=description,
                               intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')


@bot.event
async def on_member_join(member: discord.Member):
    def check(m):
        return m.author.id == member.id and bool(m.content)

    await member.timeout(datetime.timedelta(minutes=1))
    cap = captcha.generate_captcha()

    await member.send(f'Welcome {member.name}!\nPlease solve the captcha')
    await member.send(f'What is the result of the following statement?\n{cap[0]}\n\n'
                      'You only have one chance to answer, please be careful.')

    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
        if msg.content == cap[1]:
            await member.send('Thank you, enjoy the server.')
            await member.timeout(datetime.timedelta())
        else:
            raise asyncio.TimeoutError()

    except asyncio.TimeoutError:
        await member.send("You didn't solve the captcha, so we decided to kick you.")
        await member.kick()


bot.run(os.getenv('BOT_TOEKN'))
