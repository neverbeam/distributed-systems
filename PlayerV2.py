"""
-- Player Control --
Date Created: 3 December 2018
"""

import random

class Player:

    # Constant Variables
    MIN_USER_AP = 1
    MAX_USER_AP = 10
    MIN_USER_HP = 10
    MAX_USER_HP = 20
    MIN_DRAGON_AP = 5
    MAX_DRAGON_AP = 20
    MIN_DRAGON_HP = 50
    MAX_DRAGON_HP = 100
    MAX_HEAL_DIST = 5
    MAX_ATT_DIST = 2

    def __init__(self, ID, type, x, y):
        self.ID = ID
        self.type = type
        self.x = x
        self.y = y
        if type == 'user':
            self.max_hp = random.randint(MIN_USER_HP,MAX_USER_HP)
            self.ap = random.randint(MIN_USER_AP,MAX_USER_AP)
            self.hp = max_hp
        elif type == 'dragon':
            self.hp = random.randint(MIN_DRAGON_HP,MAX_DRAGON_HP)
            self.ap = random.randint(MIN_DRAGON_AP,MAX_DRAGON_AP)

    def get_distance(player):
        return math.abs(self.x - player.x) + math.abs(self.y - player.y)

    def attack_player(victim):
        distance = get_distance(victim)

        if distance > MAX_ATT_DIST:
            print("Error: Attack not valid! Distance is grater than 2.")
        else:
            victim.hp -= self.ap
            if victim.hp <= 0:
                print("Victim is dead! Remove victim from game.")

    def heal_player(player):
        distance = get_distance(player)

        if distance > MAX_HEAL_DIST:
            print("Error: Healing invalid! Distance is greater than 5.")

        if player.type == 'dragon':
            print("Error: Healing invalid! Cannot heal a dragon.")
        else:
            heal_amount = self.ap
            player.hp += heal_amount

            if player.hp >= player.max_hp:
                player.hp = player.max_hp

    def move_player(direction):

        if direction == "up":
            if self.y == board.height:
                print("Error: Invalid move! Cannot move up, player on the edge.")
            else:
                self.y += 1
        elif direction == "down":
            if self.y == 0:
                print("Error: Invalid move! Cannot move down, player on the edge.")
            else:
                self.y -= 1
        elif direction == "left":
            if self.x == 0:
                print("Error: Invalid move! Cannot move left, player on the edge.")
            else:
                self.x -= 1
        elif direction == "right":
            if self.x == board.width:
                print("Error: Invalid move! Cannot move right, player on the edge.")
            else:
                self.x += 1

    def connect_player():
        """A function to connect a player to a game""""

    def disconnect_player():
        """A function to disconnect player from a game"""
