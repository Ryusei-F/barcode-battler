#-*- coding: utf-8 -*-
import os
import traceback

import discord
from discord.ext import commands

import barcode_class


#TOKEN = os.environ['DISCORD_BOT_TOKEN']
bot = commands.Bot(command_prefix='$')

bm = barcode_class.BattleManager()

@bot.event
async def on_ready():
    print('Connected to Discord.')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.url.endswith(("png", "jpg", "jpeg")):
                player = message.author.mention
                seeds = barcode_class.convert_image_to_seeds(attachment.url)
                if seeds:
                    bm.updatePlayerList(player, seeds)
                    await message.channel.send(bm.getStatus(player))
                else:
                    await message.channel.send('バーコードを送信してね')

    await bot.process_commands(message)


@bot.command()
async def plist(ctx):
    await ctx.send(bm.getPlayerList())

@bot.command()
async def battle(ctx):
    if ctx.author.mention in bm.getPlayerList():
        if bm.getQ() == []:
            await ctx.send(bm.addBattleQueue(ctx.author.mention))
        else:
            await ctx.send(bm.addBattleQueue(ctx.author.mention))
            hp_bar_str = bm.getBattle().getHpBar()
            await ctx.send(hp_bar_str)
            for i in range(4):
                damage_str = bm.getBattle().attackEachPlayer()
                tmp = bm.getBattle().getHpBar()
                if hp_bar_str != tmp:
                    hp_bar_str = tmp
                    await ctx.send(damage_str)
                    await ctx.send(hp_bar_str)
            #if hp_bar[0][0] == '-' and hp_bar[1][0] == '-':
            #    results = 'Draw'
            #elif hp_bar[0][0] == '-':
            #    results = 'P2 Win'
            #elif hp_bar[1][0] == '-':
            #    results = 'P1 Win'
            #await ctx.send(results)
            bm.setBattleByNone()
    else:
        await ctx.send('バーコードを画像を送信してね')

@bot.command()
async def status(ctx):
    if ctx.author.mention in bm.getPlayerList():
        await ctx.send(bm.getStatus(ctx.author.mention))
    else:
        await ctx.send('バーコードを送信してね')

    
bot.run(TOKEN)

