"""
Author: Kevin Rojer & Ali Almoshawah
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

    def attack(self, victim):
        """ Attack another player and remove if they have no hp left."""
        distance = self.get_distance(victim)

        if distance > 2:
            print("Error: Attack not valid! Distance is grater than 2.")
        else:
            victim.hp -= self.ap
            if victim.hp <= 0:
                print("Victim is dead! Remove victim from game.")
                self.game.remove_player(victim)


    def get_distance(self, victim):
        return abs(self.x - victim.x) + abs(self.y - victim.y)


class Dragon(User):

    def __init__(self, ID, x, y, game):
        Character.__init__(self)
        self.type = "Dragon"
        self.max_hp = random.randint(50,100)
        self.ap = random.randint(5,20)
        self.hp = self.max_hp

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
            if self.y == board.height or self.y+1 != "!*":
                print("Error: Invalid move! Cannot move up, player on the edge.")
            else:
                self.y += 1
        elif direction == "down":
            if self.y == 0 or self.y-1 != "!*":
                print("Error: Invalid move! Cannot move down, player on the edge.")
            else:
                self.y -= 1
        elif direction == "left":
            if self.x == 0 or self.x+1 != "!*":
                print("Error: Invalid move! Cannot move left, player on the edge.")
            else:
                self.x -= 1
        elif direction == "right":
            if self.x == board.width or self.x-1 != "!*":
                print("Error: Invalid move! Cannot move right, player on the edge.")
            else:
                self.x += 1

    def heal_player(self, player):
        """ heal another player. """
        distance = self.get_distance(player)

        if distance > 5:
            print("Error: Healing failed! Distance is greater than 5.")
        else:
            heal_amount = min(self.ap, player.max_hp - player.hp)
            player.hp += heal_amount
            self.ap -= heal_amount
