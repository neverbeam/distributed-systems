"""
Author: Kevin Rojer & Ali Almoshawah
Version: 1.0
Date: 3 December 2018
"""

import random

class User:

    def __init__(self, ID, type, x, y):
        self.ID = ID
        self.type = type
        self.x = x
        self.y =  y

    def attack(victim):
        distance = get_distance(victim)

        if distance > 2:
            print("Error: Attack not valid! Distance is grater than 2.")
        else:
            victim.hp -= self.ap
            if victim.hp <= 0:
                print("Victim is dead! Remove victim from game.")

    def get_distance(victim):
        return math.abs(self.x - victim.x) + math.abs(self.y - victim.y)


class Dragon(User):

    def __init__(self, ID, x, y,):
        Character.__init__(self)
        self.ID = ID
        self.max_hp = random.randint(50,100)
        self.ap = random.randint(5,20)
        self.hp = self.max_hp

class Player(Character):

    def __init__(self, ID, x, y):
        Character.__init__(self):
        self.ID = ID
        self.max_hp = random.randint(10,20)
        self.ap = random.randint(1,10)
        self.hp = self.max_hp

    def move_player(direction):
        if direction == "up":
            self.y += 1
        elif direction == "down":
            self.y -= 1
        elif direction == "right":
            self.x += 1
        elif direction == "left":
            self.x -= 1

    def heal_player(player):
        distance = self.get_distance(player)

        if distance > 5:
            print("Error: Healing failed! Distance is greater than 5.")
        else:
            heal_amount = self.ap
            player.hp += heal_amount
            if player.hp > player.max_hp:
                player.hp = player.max_hp
