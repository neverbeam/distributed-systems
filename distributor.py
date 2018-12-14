import socket
import select
import random
import time

class Distributor:
    def __init__(self, port=11000, life_time=1100):
        # setup communication on this port
        self.own_port = port
        self.life_time = life_time
        # list of active game servers
        self.servers = []

    # add a server port to the server list
    def add_server(self, server_port):
        # each server has a port, player number (TODO and location)
        server = [server_port, 0]
        self.servers.append(server)

    # look for the best server port for a new player
    def add_player(self):
        best_server = None
        # check all known servers
        for server in self.servers:
            # find the server with the lowest number of players
            if best_server == None or best_server[1] > server[1]:
                best_server = server

        # TODO get the player number dynamicly by communicating with servers
        best_server[1] += 1 # add 1 to the servers player count

        # send the player to the best server
        return best_server


    # run this as a daemon to receive player join requests
    def handle_messages(self):
        pass
