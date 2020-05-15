#-*- coding: utf-8 -*-
import os
import traceback
import discord
from discord.ext import commands
from dotenv import load_dotenv

INITIAL_EXTENSIONS = [
    'cogs.cog'
]

class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()


if __name__ == '__main__':
    load_dotenv()
    discord_token = os.getenv('TOKEN')
    bot = MyBot(command_prefix='>')
    bot.run(discord_token)
