import socket
import select
import random
import time
import math
import numpy as np

class Distributor:
    def __init__(self, port=11000, life_time=1100, printing=True, speedup=1):
        # setup communication on this port
        self.own_port = port
        self.life_time = life_time
        self.start_time = time.time()
        self.speedup = speedup
        # list of active game servers
        self.servers = []
        self.init_socket()
        # this only for experiments
        self.latencies = []

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
        if len(self.latencies) > 0:
            print(self.latencies)
            print(np.mean(self.latencies))
            print(np.std(self.latencies))

    # add a server port to the server list
    def add_server(self, server_port, peer_port, lat, lng):
        # each server has a port, player number (TODO and location)
        server = [server_port, peer_port, lat, lng, 0]
        self.servers.append(server)

    # remove a server from the server list
    def remove_server(self, server_port):
        for i in range(len(self.servers)):
            if self.servers[i][0] == server_port:
                self.servers.pop(i)
                break

    # look for the best server port for a new player
    def add_player(self, lat, lng):
        best_server = None
        best_distance_players = None
        # check all known servers
        for server in self.servers:
            # get the euclidean distance
            distance = math.sqrt((server[2] - lat)**2 + (server[3] - lng)**2)
            players = server[4]+1
            # find the server with the lowest number of players * distance (is on index 2)
            if best_server == None or best_distance_players > (players*(distance+0.1)):
                best_server = server
                best_distance_players = players*(distance+0.1)

        # set it, but also get the player number dynamicly by communicating with servers
        best_server[4] += 1 # add 1 to the servers player count
        # prevent errors, but report on the closest server
        best_distance = 0 if best_distance_players == None else best_distance_players/(best_server[4])

        # send the player to the best server on the client port
        return best_server[0], best_distance

    def update_player_total(self, server_port, new_player_total):
        the_server = None
        # check all known servers
        for server in self.servers:
            # find the server with the matching port
            if server[0] == server_port:
                the_server = server
                break

        print("Server on port ", the_server[0], "players=", the_server[4], "->", new_player_total)
        the_server[4] = new_player_total


    # run this as a daemon to receive player join requests
    def read_ports(self):
        """ Read the sockets for new connections or player noticeses."""
        self.sock.settimeout(1/self.speedup)
        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)*self.speedup):
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
                            client_data = message.split("|")
                            if len(client_data) != 2:
                                # ill defined message
                                pass
                            else:
                                # get the latitude and longitude of the client from the message
                                lat_lng = client_data[1].split(";")
                                lat = float(lat_lng[0])
                                lng = float(lat_lng[1])
                                if len(self.servers) > 0:
                                    # get the best server for this player
                                    server_port, distance = self.add_player(lat, lng)
                                    distance_str = "{:.4f}".format(distance)
                                    self.latencies.append(distance)
                                    # send this server port to the client
                                    ret_mess = ('DIST|' + str(server_port) + "|" + distance_str).encode('UTF-8')
                                    conn.sendall(ret_mess)
                                else: 
                                    # TODO start up a server
                                    conn.sendall(b'NO_SERVER')

                        # check for server message about its player total
                        elif message.startswith('SERVER|'):
                            server_stats = message.split("|")
                            if len(server_stats) != 3:
                                # ill defined message
                                pass
                            else:
                                try:
                                    # get the servers, so we know which one it is
                                    server_port = int(server_stats[1])
                                    # set the given player total
                                    new_player_total = int(server_stats[2])
                                    self.update_player_total(server_port, new_player_total)
                                except ValueError:
                                    # message was not an integer
                                    pass

                        # handles the first message of a new server
                        elif message.startswith('NEW_SERVER|'):
                            new_server_mess = message.split("|")
                            if len(new_server_mess) != 4:
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
                                    conn.sendall(ret_mess)

                                    # get the latitude and longitude of the server from the message
                                    lat_lng = new_server_mess[3].split(";")
                                    lat = float(lat_lng[0])
                                    lng = float(lat_lng[1])

                                    # add the server to the lists
                                    self.add_server(new_server_port, new_server_peer_port, lat, lng)
                                except ValueError:
                                    # message was not an integer
                                    pass

                        # check for server message about him stopping
                        elif message.startswith('OUT_SERVER|'):
                            server_stats = message.split("|")
                            if len(server_stats) != 2:
                                # ill defined message
                                pass
                            else:
                                try:
                                    # remove the server
                                    server_port = int(server_stats[1])
                                    self.remove_server(server_port)
                                    print("Distributor removed server, updated = ", self.servers)
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


if __name__ == '__main__':
    import sys
    listen_port = int(sys.argv[1])
    run_time = int(sys.argv[2])
    d = Distributor(port=listen_port, life_time=run_time)
    print("Created distributor process " + str(listen_port))
    # let the distributor listen to all incoming messages until lifetime is up
    d.read_ports()
    print("Distributor closed on port " + str(listen_port))