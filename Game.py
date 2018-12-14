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
        self.width = 25 + 1
        self.height = 25 + 1
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
        # TODO: Perhaps make some individual functions here
        # move;player;up/down/left/rigth
        data = data.split(";")
        print(data)
        if data[0] == "move":
            player = self.players[data[1]]
            self.map[player.y][player.x] = "*"
            player.move_player(data[2]) # Perhaps do some error checking here
            self.map[player.y][player.x] = player
            print("new coordinates", player.y, player.x)
        # attack;player1;player2
        elif data[0] == "attack":
            player1 = self.players[data[1]]
            player2 = self.players[data[2]]
            player1.attack(player2)
        elif data[0] == "join":
            player = Player(data[1], int(data[2]), int(data[3]), self)
            player.hp = int(data[4])
            player.ap = int(data[5])
            self.players[data[1]]=player
        elif data[0] == "heal":
            player1 = self.players[data[1]]
            player2 = self.players[data[2]]
            player1.heal_player(player2)

        else:
            print("Not a valid command")





    # what is the idea of this?
    # def remove_player_id(self, ID):
    #     for x in range(self.width):
    #         for y in range(self.height):
    #             if self.map[x][y] != "*" and self.map[x][y].id == ID:
    #                 self.remove_user(x, y)
