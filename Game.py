"""
Author: Kevin Rojer
Version: 1.0
Date: 30 November 2018
"""

from Player import *
import client

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
            print("Player ({0}) with hp {1} added to the game at position ({2},{3}).".format(player.ID, player.hp, player.x, player.y))
        else:
            print("Error: Position ({0},{1}) is occupied.".format(player.x, player.y))

    def remove_player(self, player):
        """ Remove players from the grid."""
        y = player.y
        x = player.x
        if self.map[y][x] == "*":
            print("Error: Cannot remove player, spot {} {} is empty {}.".format(player.y, player.x, player.ID))
        else:
            del self.players[player.ID]
            self.map[y][x] = "*"


    # def disconnect_player(self, player):
    #     """ Disconnect a player that is dead"""
    #     if isinstance(self.upper, client.Client) and self.upper.myplayer.ID == player.ID:
    #         self.upper.keep_alive = 0


    def update_grid(self, data):
        """Update my grid"""
        print ("UPDATING GRID WITH: ", data)
        # timestamp;move;player;up/down/left/rigth
        data = data.split(";")[1:]

        try:
            if data[0] == "move":
                player = self.players[data[1]]
                self.map[player.y][player.x] = "*"
                if player.move_player(data[2]):
                    self.map[player.y][player.x] = player
                    print("new coordinates", player.ID, player.y, player.x)
                    return 1
                else:
                    self.map[player.y][player.x] = player
                    return 0
            # attack;player1;player2
            elif data[0] == "attack":
                player1 = self.players[data[1]]
                player2 = self.players[data[2]]
                if player1.attack(player2):
                    return 1
                else:
                    return 0
            # join;playerid;x;y;hp;ap
            elif data[0] == "join":
                player = Player(data[1], int(data[2]), int(data[3]), self)
                player.hp = int(data[4])
                player.ap = int(data[5])
                self.players[data[1]]=player
                return 1
            elif data[0] == "leave":
                player = self.players[data[1]]
                self.remove_player(player)
                return 1
            elif data[0] == "heal":
                player1 = self.players[data[1]]
                player2 = self.players[data[2]]
                if player1.heal_player(player2):
                    return 1
                return 0

            else:
                print("Not a valid command:", data)
                return 0
        except(KeyError):
            return 0
