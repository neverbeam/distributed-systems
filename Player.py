"""
Author: Kevin Rojer & Ali Almoshawah
Version: 1.0
Date: 30 November 2018
"""

import random
import

class Character:

    def __init__(self, x, y, ID):
        self.hp = 1
        self.ap = 1
        self.x = x
        self.y =  y
        self.ID = ID
        self.type = "character"

    def move_player(direction):
        if direction == "up":
            self.y += 1

        elif direction == "down":
            self.y -= 1
        elif direction == "right":
            self.x += 1
        elif direction == "left":
            self.x -= 1

    def is_move_valid(direction):


    def attack(character):

        if is_attack_valid(character):
            character.hp = character.hp - self.ap
        else:
            print("Attack not valid!")


    def is_attack_valid(character):
        horiz_diff = self.x - character.x
        vert_diff = self.y - character.y

        if horiz_diff in range(-2,2) and vert_diff in range(-2,2):
            return True

        return False




class Dragon(Character):

    def __init__(self, ID, x, y,):
        Character.__init__(self)
        self.hp = random.randint(50,100)
        self.ap = random.randint(5,20)
        self.ID = ID
        self.x = x
        self.y = y

class Player(Character):

    def __init__(self, ID, x, y):
        Character.__init__(self):
        self.hp = random.randint(10,20)
        self.ap = random.randint(1,10)
        self.ID = ID
        self.x = x
        self.y = y

    def heal_player():
        "A player can only heal a player within two squares"
         heal_amount = self.ap

        
