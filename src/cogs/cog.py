#-*- coding: utf-8 -*-
import discord
import os
from discord.ext import commands
from . import barcode
from . import boss

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.raid_num = 0
        self.boss = boss.Boss(self.raid_num)
        self.manager = barcode.BattleManager()

    @commands.command()
    async def list(self, ctx):
        if self.manager.getPlayerList() == []:
            await ctx.send('参加者はいません')
        else:
            await ctx.send('参加者: {}'.format(self.manager.getPlayerList()))

    @commands.command()
    async def status(self, ctx):
        if ctx.author.name in self.manager.getPlayerList():
            await ctx.send(self.manager.getStatus(ctx.author.name))
        else:
            await ctx.send('バーコード画像を送信してください')
        
    @commands.command()
    async def battle(self, ctx):
        if ctx.author.name in self.manager.getPlayerList():
            if self.manager.hasWaitingPlayer(ctx.author.name):
                embed = self.manager.getBattle().getEachStatus()
                await ctx.send(embed = embed)
            else:
                await ctx.send('対戦待機中')
        else:
            await ctx.send('バーコードを送信してね')

    @commands.command()
    async def score(self, ctx):
        if self.manager.getPlayerList() != []:
            score = self.manager.getScore()
            await ctx.send(score)
        else:
            await ctx.send('参加者はいません')

    @commands.command()
    async def concede(self, ctx):
        if self.manager.existsBattle():
            if self.manager.concede(ctx.author.name):
                await ctx.send('対戦終了')
            
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.attachments:
            for attachment in message.attachments:
                if attachment.url.endswith(("png", "jpg", "jpeg")):
                    name = message.author.name
                    seeds = barcode.convert_image_to_seeds(attachment.url)
                    if seeds:
                        self.manager.updatePlayerList(name, seeds)
                        await message.channel.send(self.manager.getStatus(name))

                        self.boss.attackedBy(self.manager.getPlayer(name))
                        if self.boss.getHp() > 0:
                            send_str = 'レイドボス{} ({} / {}) \n'.format(self.raid_num+1, self.boss.getHp(), self.boss.getdHp())
                            send_str += '[||' + '　' * self.boss.ratio_of_hp() + '||' + '　' * (10 - self.boss.ratio_of_hp()) + ']'
                            await message.channel.send(send_str)
                        if self.boss.getHp() <= 0:
                            await message.channel.send('``` レイドボス{}討伐成功 ```'.format(self.raid_num+1))
                            self.raid_num += 1
                            self.boss = boss.Boss(self.raid_num)


        if message.content:
            if self.manager.existsBattle():
                if message.author.name in self.manager.getMatchedPlayer():
                    try:
                        command = int(message.content.split(" ", 1)[0])
                        results = self.manager.insertCommandQ(message.author.name, command)
                        if results != None:
                            if results != 'next':
                                await message.channel.send('```{}```'.format(results))
                            else:
                                embed = self.manager.getBattle().getEachStatus()
                                await message.channel.send(embed = embed)
                    except ValueError:
                        return

    @commands.Cog.listener()
    async def on_ready(self):
        print('Connected to Discord.')


def setup(bot):
    bot.add_cog(Commands(bot))
