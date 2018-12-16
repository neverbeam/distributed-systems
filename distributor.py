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
        dist_address = ('localhost', self.own_port)
        print('Distributor starting up on {} port {}'.format(*dist_address))
        self.sock.bind(dist_address)
        # allow 10 connections at the same time, so that they wait for eachother
        self.sock.listen(10)

    def power_down(self):
        """ Close down the distributor. """
        self.sock.close()

    # add a server port to the server list
    def add_server(self, server_port, peer_port):
        # each server has a port, player number (TODO and location)
        server = [server_port, peer_port, 0]
        self.servers.append(server)

    # look for the best server port for a new player
    def add_player(self):
        best_server = None
        # check all known servers
        for server in self.servers:
            # find the server with the lowest number of players (is on index 2)
            if best_server == None or best_server[2] > server[2]:
                best_server = server

        # TODO get the player number dynamicly by communicating with servers
        best_server[2] += 1 # add 1 to the servers player count

        # send the player to the best server on the client port
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

                        # check for client connection to send him to a server
                        if message.startswith('CLIENT|'):
                            # get the best server for this player
                            server_port = self.add_player()
                            # send this server port to the client
                            ret_mess = ('DIST|' + str(server_port)).encode('UTF-8')
                            conn.sendall(ret_mess)

                        # check for server message about its player total
                        elif message.startswith('SERVER|'):
                            server_stats = message.split("|")
                            if len(server_stats) != 2:
                                # ill defined message
                                pass
                            else:
                                try:
                                    # set the given player total
                                    new_player_total = int(server_stats[1])
                                    print("Updated player total", new_player_total)
                                except ValueError:
                                    # message was not an integer
                                    pass

                        # handles the first message of a new server
                        elif message.startswith('NEW_SERVER|'):
                            new_server_mess = message.split("|")
                            if len(new_server_mess) != 3:
                                # ill defined mdist
                                pass
                            else:
                                try:
                                    # get the client port and peer port of the server
                                    new_server_port = int(new_server_mess[1])
                                    new_server_peer_port = int(new_server_mess[2])

                                    # send back the peers that the server has
                                    ret_mess = 'DIST'
                                    if len(self.servers) == 0:
                                        # has no peers yet so let server know that he has to start the game
                                        ret_mess += '|NO_PEERS'
                                    else:
                                        for server in self.servers:
                                            # the peer server ports are saved at index 1
                                            peer_server_port = server[1]
                                            ret_mess += '|' + str(peer_server_port)
                                    ret_mess = ret_mess.encode('UTF-8')
                                    print(ret_mess)
                                    conn.sendall(ret_mess)

                                    # add the server to the lists
                                    self.add_server(new_server_port, new_server_peer_port)
                                except ValueError:
                                    # message was not an integer
                                    pass
                        else:
                            # junk message
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
