#!/usr/bin/env python

import discord
import discord.ext.commands
import os

description = "Captcha bot"

intents = discord.Intents.default()
intents.bans = True
intents.members = True
intents.message_content = True

bot = discord.ext.commands.Bot(command_prefix='!',
                               description=description,
                               intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')


@bot.event
async def on_member_join(member: discord.Member):
    await member.send(f'Welcome {member.name}!')


bot.run(os.getenv('BOT_TOEKN'))
