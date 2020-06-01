import math

class Boss():
    def __init__(self, raid_num):
        self.default_hp = 20000 * (2 ** raid_num)
        self.hp = 20000 * (2 ** raid_num)
        self.atk = 20000

    def attackedBy(self, player):
        num_of_atks = math.ceil(player.getHp() / self.atk)
        self.hp = (self.hp - player.getAtk() * num_of_atks) if (self.hp - player.getAtk() * num_of_atks) > 0 else 0

    def ratio_of_hp(self):
        return round(self.hp * 10 / self.default_hp)

    def getdHp(self):
        return self.default_hp

    def getHp(self):
        return self.hp