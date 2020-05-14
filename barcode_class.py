#-*- coding: utf-8 -*-
from PIL import Image
import zbarlight
import queue
import random
import requests
import io

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
        self.player_list = {}

    def updatePlayerList(self, player_name, player_seed):
        dict = {player_name: Player(player_name, player_seed)}
        self.player_list.update(dict)

    def getPlayerList(self):
        return list(self.player_list.keys())

    def addBattleQueue(self, player_name):
        if self.q == []:
            self.q.append(self.player_list[player_name])
            return ('対戦相手を待っています')
        else:
            self.battle = Battle(self.q.pop(0), self.player_list[player_name])
            return ('対戦開始')

    def hasPlayer(self, player_name):
        return (player_name in self.player_list.keys())

    def getStatus(self, player_name):
        return self.player_list[player_name].getStatus()

    def getQ(self):
        return self.q
    
    def getBattle(self):
        return self.battle

    def setBattleByNone(self):
        self.battle = None
        

class Battle:
    def __init__(self, p1, p2):
        self.p1Name = p1.getPlayerName()
        self.p2Name = p2.getPlayerName()
        self.maxHpP1 = p1.getHp()
        self.maxHpP2 = p2.getHp()
        self.hp_bar = ['+' * 10, '+' * 10]
        self.p1 = [p1.getHp(), p1.getAtk(), int(p1.getDef() / 10)]
        self.p2 = [p1.getHp(), p2.getAtk(), int(p2.getDef() / 10)]
        self.damage = [0, 0]
        self.step = 3/4

    def attackEachPlayer(self):
        self.damage = [0, 0]
        while not( (self.maxHpP1 - self.damage[0] <= self.step * self.maxHpP1)
        or (self.maxHpP2 - self.damage[1] <= self.step * self.maxHpP2)):
            self.damage[0] += int(self.p2[1] / self.p1[2])
            self.damage[1] += int(self.p1[1] / self.p2[2])

        
        self.p1[0] = max(0, self.p1[0] - self.damage[0])
        self.p2[0] = max(0, self.p2[0] - self.damage[1])
        
        if self.p1[0] <= self.step * self.maxHpP1 or self.p2[0] <= self.step * self.maxHpP2:
            self.step -= 1/4
        damage_str = self.p1Name + " takes {} points of damage,".format(self.damage[0]) + self.p2Name + " takes {} points of damage".format(self.damage[1])
        return damage_str

    def getHpBar(self):
        par_p1 = round(self.p1[0] / self.maxHpP1 * 10)
        par_p2 = round(self.p2[0] / self.maxHpP2 * 10)
        self.hp_bar[0] = self.hp_bar[0][0:par_p1] + '-' * (10 - par_p1)
        self.hp_bar[1] = self.hp_bar[1][0:par_p2] + '-' * (10 - par_p2)
        hp_bar_str = "{:>10}: [{:>10}], \n".format(self.p1Name, self.hp_bar[0]) + "{:>10}: [{:>10}]".format(self.p2Name, self.hp_bar[1])
        return hp_bar_str
    
class Player:
    def __init__(self, binNum):
        random.seed(binNum)
        self.val = [round(random.randint(1, 10000),-1) for i in range(3)]

    def __init__(self, player_name, binNum):
        self.player_name = player_name
        random.seed(binNum)
        self.val = [round(random.randint(1, 10000),-1) for i in range(3)]

    def getStatus(self):
        return "HP:{:>5},ATK:{:>5},DEF:{:>5}".format(self.val[0], self.val[1], self.val[2])
        
    def getHp(self):
        return self.val[0]

    def getAtk(self):
        return self.val[1]

    def getDef(self):
        return self.val[2]

    def setStatus(self, val):
        self.val = val

    def getPlayerName(self):
        return self.player_name
