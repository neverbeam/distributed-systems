"""
Author: Kevin Rojer & Ali Almoshawah
Version: 1.0
Date: 30 November 2018
"""

import Arena
import Player
import Dragon

class Game:

    def __init__(self, ID, width, height, max_player, max_dragon):
        self.ID = ID
        self.width = width
        self.height = height
        self.max_players = max_player
        self.max_dragons = max_dragon
        self.map = [["*" for j in range(self.width)] for i in range(self.height)]
        self.players = []

    def add_player():


    def remove_player(self, x, y):
        if self.map[y][x] == "*":
            print("Error: Cannot remove player, spot is empty.")
        else:
            self.players.remove(self.map[y][x])
            self.map[y][x] = "*"

    def remove_player_id(self, ID):
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y] != "*" and self.map[x][y].id == ID:
                    self.remove_user(x, y)
