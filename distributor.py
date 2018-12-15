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
    def init_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', self.own_port)
        print('Distributor starting up on {} port {}'.format(*server_address))
        self.sock.bind(server_address)
        # allow 10 connections at the same time, so that they wait for eachother
        self.sock.listen(10)

    def power_down(self):
        """ Close down the distributor. """
        self.sock.close()

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
        return best_server[0]


    # run this as a daemon to receive player join requests
    def read_ports(self):
        """ Read the sockets for new connections or player noticeses."""
        self.sock.settimeout(1)
        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)):
            try:
                # open up a new socket to communicate with this messager
                conn, addr = self.sock.accept()
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        message = data.decode('utf-8')

                        # check for either client connection or server stats message
                        if message.startswith('CLIENT|'):
                            print(self.servers)
                            # get the best server for this player
                            server_port = self.add_player()
                            # send this server port to the client
                            ret_mess = ('DIST|' + str(server_port)).encode('UTF-8')
                            conn.sendall(ret_mess)
                        elif message.startswith('SERVER|'):
                            server_stats = message.split("|")
                            if len(server_stats) < 2 or len(server_stats) > 2:
                                # ill defined message
                                pass
                            else:
                                try:
                                    new_player_total = int(server_stats[1])
                                    print(new_player_total)
                                except ValueError:
                                    # message was not an integer
                                    pass
                        elif message.startswith('NEW_SERVER|'):
                            new_server_mess = message.split("|")
                            if len(new_server_mess) < 2 or len(new_server_mess) > 2:
                                # ill defined message
                                pass
                            else:
                                try:
                                    new_server_port = int(new_server_mess[1])
                                    self.add_server(new_server_port)
                                except ValueError:
                                    # message was not an integer
                                    pass
                

            # Handling stopping distributor
            except KeyboardInterrupt:
                # self.power_down()
                break

            # no message in set timeout, try again
            except socket.timeout:
                pass

        # always power down for right now
        print("Distributor shutting down")
        self.power_down()
