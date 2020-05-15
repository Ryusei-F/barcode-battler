#-*- coding: utf-8 -*-
from PIL import Image
import zbarlight
import queue
import random
import requests
import io
import discord
from discord.ext import commands

def convert_image_to_seeds(url):
    image = Image.open(io.BytesIO(requests.get(url).content))
    codes = zbarlight.scan_codes(['ean13'], image)
    if codes != None:
        return (int(codes[0].decode()))
    else:
        return False

class BattleManager:
    def __init__(self):
        self.battle = None
        self.q = []
        self.commandq = {}
        self.player_list = {}

    def updatePlayerList(self, player_name, player_seed):
        if player_name not in self.player_list:
            win_count = 0
        else :
            win_count = self.player_list[player_name][1]
        dict = {player_name: [Player(player_name, player_seed), win_count]}
        self.player_list.update(dict)

    def getPlayerList(self):
        return list(self.player_list.keys())

    def hasWaitingPlayer(self, player_name):
        if self.q == []:
            self.q.append(self.player_list[player_name][0])
            return False
        else:
            if self.player_list[player_name][0] not in self.q:
                if len(self.q) == 1: 
                    self.q.append(self.player_list[player_name][0])
                    self.battle = Battle(self.q[0], self.q[1])
                    return True
            else:
                return False

    def insertCommandQ(self, player_name, command):
        self.commandq.update({player_name: command})
        if len(self.commandq) == 2:
            results = self.battle.actionByCommand(self.commandq)
            if results != 'next':
                if results == "Winner {}".format(self.q[0].getName()):
                    self.player_list[self.q[0].getName()][1] += 1
                elif results == "Winner {}".format(self.q[1].getName()):
                    self.player_list[self.q[1].getName()][1] += 1
                self.battle.resetStatus()
                self.battle = None
                self.q.clear()
                self.commandq.clear()
                
            return results
        else:
            return None

    def concede(self, player_name):
        if player_name in self.battle.getPlayerNameList():
            opp_name = {player_name} ^ set(self.battle.getPlayerNameList())
            opp_name = (list(opp_name))[0]
            self.player_list[opp_name][1] += 1

            self.battle.resetStatus()
            self.battle = None
            self.q.clear()
            self.commandq.clear()
            return True
        else:
            return False
                
    def hasPlayer(self, player_name):
        return (player_name in self.player_list.keys())

    def getStatus(self, player_name):
        return self.player_list[player_name][0].getStatus()

    def getMatchedPlayer(self):
        if self.battle != None:
            return self.battle.getPlayerNameList()
    
    def getBattle(self):
        return self.battle

    def setBattleByNone(self):
        self.battle = None

    def existsBattle(self):
        return self.battle != None

    def getScore(self):
        score = "```"
        for key in self.player_list:
            score += (f'{key}').ljust(10) + ":" + (f'{self.player_list[key][1]}').center(10) + "wins\n"
        score += "```"
        return score
        

class Battle:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def getEachStatus(self):
        embed = discord.Embed(title="Battle! (数字を入力)",description="・Win\t:  ATK *= 2\n・Draw\t: Attack your opponent\n・Lose\t: ATK /= (10000 - DEF)/100\n\n where 0 (mod 3) < 1 (mod 3) < 2 (mod 3) < 0 (mod 3),\n      x (mod 3) = x (mod 3) for any x")
        embed.add_field(name=self.p1.getName(), value=self.p1.getStatus(), inline=False)
        embed.add_field(name=self.p2.getName(), value=self.p2.getStatus(), inline=False)
        
        return embed

    def actionByCommand(self, commandq):
        act1 = commandq.pop(self.p1.getName()) % 3
        act2 = commandq.pop(self.p2.getName()) % 3 
        if (act1 + 1) % 3  == act2:
            self.p2.setAtk(self.p2.getAtk() * 2)
            self.p1.setAtk(max(1, self.p1.getAtk() / ((10000 - self.p1.getDef())/100)))
        elif (act1 + 2) % 3 == act2:
            self.p1.setAtk(self.p1.getAtk() * 2)
            self.p2.setAtk(max(1, self.p2.getAtk() / ((10000 - self.p2.getDef())/100)))
        self.p1.setHp(self.p1.getHp() - self.p2.getAtk())
        self.p2.setHp(self.p2.getHp() - self.p1.getAtk())

        results = "next"
        if self.p1.getHp() <= 0 and self.p2.getHp() <= 0:
            results = 'Draw'
        elif self.p1.getHp() <= 0:
            results = "Winner {}".format(self.p2.getName())
        elif self.p2.getHp() <= 0:
            results = "Winner {}".format(self.p1.getName())
            
        return results

    def getPlayerNameList(self):
        return [self.p1.getName(), self.p2.getName()]

    def resetStatus(self):
        self.p1.resetStatus()
        self.p2.resetStatus()
    
class Player:
    def __init__(self, player_name, seeds):
        self.player_name = player_name
        random.seed(seeds)
        self.val = [0 for i in range(3)]
        self.val[0] = round(random.randint(5000, 50000), -2)
        self.val[1] = round(random.randint(500, 10000), -1)
        self.val[2] = round(random.randint(500, 10000), -1)
        self.originalVal = list(self.val)
        
    def getStatus(self):
        return "HP:{:>5}/{:>5}, ATK:{:>}/{:>5} ,DEF:{:>5}".format(self.val[0], self.originalVal[0], self.val[1], self.originalVal[1], self.val[2])

    def setHp(self, hp):
        self.val[0] = int(hp)

    def setAtk(self, atk):
        self.val[1] = int(atk)
        
    def getHp(self):
        return self.val[0]

    def getAtk(self):
        return self.val[1]

    def getDef(self):
        return self.val[2]

    def resetStatus(self):
        self.val = list(self.originalVal)

    def getName(self):
        return self.player_name
