"""
Author: Kevin Rojer 
Version: 1.0
Date: 3 December 2018
"""

import random

class User:

    def __init__(self, ID, x, y, game):
        self.ID = ID
        self.x = x
        self.y =  y
        self.game = game
        self.maxrange = 2

    def attack(self, victim):
        """ Attack another player and remove if they have no hp left."""
        distance = self.get_distance(victim)

        if distance > self.maxrange:
            print("Error: Attack not valid! Distance is greater than max.")
            print(victim.y, victim.x, self.y, self.x, self.ID, victim.ID)
            return 0
        else:
            print("Victim {} hp: {}".format(victim.ID, victim.hp))
            victim.hp -= self.ap
            print("Victim {} hp: {}".format(victim.ID, victim.hp))
            if victim.hp <= 0:
                print("player {} is dead! Remove victim from game.".format(victim.ID))
                self.game.remove_player(victim)
            return 1


    def get_distance(self, victim):
        return (abs(self.x - victim.x) + abs(self.y - victim.y))


class Dragon(User):

    def __init__(self, ID, x, y, game):
        User.__init__(self, ID, x, y, game)
        self.type = "Dragon"
        self.max_hp = random.randint(50,100)
        self.ap = random.randint(5,20)
        self.hp = self.max_hp
        self.maxrange = 5

class Player(User):

    def __init__(self, ID, x, y, game):
        User.__init__(self, ID, x, y, game)
        self.type = "Player"
        self.max_hp = random.randint(10,20)
        self.ap = random.randint(1,10)
        self.hp = self.max_hp

    def move_player(self, direction):
        """ Move the player in the right direction. """
        if direction == "up":
            if self.y == self.game.height-1 or self.game.map[self.y+1][self.x] != "*":
                print("Error: Invalid move! cannot move up")
                return 0
            else:
                self.y += 1
                return 1
        elif direction == "down":
            if self.y == 0 or self.game.map[self.y-1][self.x] != "*":
                print("Error: Invalid move! Cannot move down")
                return 0
            else:
                self.y -= 1
                return 1
        elif direction == "left":
            if self.x == 0 or  self.game.map[self.y][self.x-1] != "*":
                print("Error: Invalid move! Cannot move left")
                return 0
            else:
                self.x -= 1
                return 1
        elif direction == "right":
            if self.x == self.game.width-1 or self.game.map[self.y][self.x+1] != "*":
                print("Error: Invalid move! Cannot move right")
                return 0
            else:
                self.x += 1
                return 1

    def heal_player(self, player):
        """ heal another player. """
        distance = self.get_distance(player)

        if distance > 5:
            print("Error: Healing failed! Distance is greater than 5.")
            return 0
        else:
            heal_amount = min(self.ap, player.max_hp - player.hp)
            player.hp += heal_amount
            self.ap -= heal_amount
            return 1
