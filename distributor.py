import socket
import select
import random
import time

class Distributor:
    def __init__(self, port=11000, life_time=1100):
        # setup communication on this port
        self.own_port = port
        self.life_time = life_time
        self.start_time = time.time()
        # list of active game servers
        self.servers = []
        self.init_socket()

    # initialize the socket to listen to on own_port
    def init_socket(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', self.own_port)
        print('starting up on {} port {}'.format(*server_address))
        self.sock.bind(server_address)
        self.connections = [self.sock]
        # allow 10 connections at the same time, so that they wait for eachother
        self.sock.listen(10)

    def power_down(self):
        """ Close down the distributor. """
        print ("Terminating and closing existing connections")
        for connection in self.connections[1:]:
            connection.close()

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
    def read_ports(self):
        """ Read the sockets for new connections or player noticeses."""
        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)):
            try:
                # Wait for a connection
                readable, writable, errored = select.select(self.connections, [], [])

                
            # Handling stopping servers and closing connections.
            except KeyboardInterrupt:
                # self.power_down()
                break

        # always power down for right now
        print("Server shutting down")
        self.power_down()
