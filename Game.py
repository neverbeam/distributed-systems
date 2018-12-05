"""
Author: Kevin Rojer & Ali Almoshawah
Version: 1.0
Date: 30 November 2018
"""

import Arena
from Player import *

class Game:

    def __init__(self, upper, ID=1, max_player=100, max_dragon=25):
        self.ID = ID
        self.width = 25
        self.height = 25
        self.max_players = max_player
        self.max_dragons = max_dragon
        self.map = [["*" for j in range(self.width)] for i in range(self.height)]
        self.players = {}
        self.upper = upper

    def add_player(self, player):
        """ Add players to the grid."""
        if self.map[player.y][player.x] == "*":
            self.map[player.y][player.x] = player
            self.players[player.ID] = player
            print("Player ({0}) added to the game at position ({1},{2}).".format(player.ID, player.x, player.y))
        else:
            print("Error: Position ({0},{1}) is occupied.".format(player.x, player.y))

    def remove_player(self, player):
        """ Remove players from the grid."""
        y = player.y
        x = player.x
        if self.map[y][x] == "*":
            print("Error: Cannot remove player, spot is empty.")
        else:
            del self.players[player.ID]
            self.map[y][x] = "*"
            # perhaps delete the instance here

    def update_grid(self, data):
        """Update my grid"""
        # TODO: Perhaps make some individual fucntions here
        if data[0] == "move":
            player = self.players[int(data[1])]
            self.map[player.y][player.x] = "*"
            player.x = int(data[2])
            player.y = int(data[3])
            self.map[int(data[3])][int(data[2])] = player

        # MOre parse functions  here

        else:
            print("Not a valid command")


    # what is the idea of this?
    def remove_player_id(self, ID):
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y] != "*" and self.map[x][y].id == ID:
                    self.remove_user(x, y)
