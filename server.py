import socket
import select
import random
import time
from Game import *
from queue import Queue, Empty
from threading import Thread
import os
import sys


class Server:
    def __init__(self, port=10000, peer_port=10100, life_time=None, check_alive=1, ID=0, lat=1, lng=1, num_dragons=1, speedup=1.0, printing=True):
        # we could also place object on a 25x25 grid
        self.port = port
        self.peer_port = peer_port
        self.lat = lat
        self.lng = lng
        self.life_time = life_time
        self.start_time = time.time()
        self.speedup = speedup
        # do not print to terminal for experiments
        self.printing = printing
        if not self.printing:
            sys.stdout = open(os.devnull, 'w')
        self.check_alive = check_alive
        self.tickdata = b''
        self.game_started = False
        self.game = Game(self, ID,2,1)
        self.ID_connection = {}
        self.server_queue = Queue()
        self.peer_queue = Queue()
        filename = 'logfile{}'.format(self.game.ID)
        self.log = open(filename,'w')

        self.start_up(num_dragons, port, peer_port)



    def start_up(self, num_dragons, port=10000, peer_port=10100):
        """ Create an server for das game. Each server will maintain a number of dragons."""
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        found_free_port = False
        while not found_free_port:
            try:
                server_address = ('localhost', self.port)
                self.sock.bind(server_address)
                print('Server starting up on {} port {}'.format(*server_address))
                found_free_port = True
                self.connections = [self.sock]
            except OSError:
                print("Given server port was in use, trying similar...")
                self.port += 10000
                if self.port >= 100000:
                    raise OSError('Cant find a suitable server port.')

        # create the set number of dragons for this server
        self.dragonlist = []
        for i in range(int(num_dragons)):
            self.create_dragon()
        # if number was float, give the residual a chance to become a dragon
        # meaning: 3.2 has a 20% chance of creating a 4th dragon
        if random.random() < (num_dragons%1):
            self.create_dragon()

        # Listen for incoming connections
        self.sock.listen(30)

        # FOR PEERS
        # Create a TCP/IP socket
        self.peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        found_free_port = False
        while not found_free_port:
            try:
                server_peer_address = ('localhost', self.peer_port)
                self.peer_sock.bind(server_peer_address)
                print('Peer server starting up on {} port {}'.format(*server_peer_address))
                found_free_port = True
                self.peer_connections = [self.peer_sock]
            except OSError:
                print("Given peer port was in use, trying similar...")
                self.peer_port += 10000
                if self.peer_port >= 100000:
                    raise OSError('Cant find a suitable peer port.')

        # Listen for incoming connections
        self.peer_sock.listen(4)


    def receive_grid(self, peer_socket):
        """ Receive the current state of the grid from the server. """
        data = ""
        # Keep receiving until an end has been send. TCP gives in order arrival
        while True:
            data += peer_socket.recv(128).decode('utf-8')
            if data[-3:] == "end":
                break

        #Parse the data so that the user contains the whole grid.
        # type, ID, x, y, hp , ap,
        data = data[:-3].split(";")
        del data[-1]
        for i in range(0, len(data), 6):
            playerdata = data[i:i+6]
            if playerdata[0] == "Player":
                player = Player(playerdata[1], int(playerdata[2]), int(playerdata[3]) ,self.game)
                player.hp = int(playerdata[4])
                player.ap = int(playerdata[5])

            elif playerdata[0] == "Dragon":
                player = Dragon(playerdata[1], int(playerdata[2]), int(playerdata[3]) ,self.game)
                player.hp = int(playerdata[4])
                player.ap = int(playerdata[5])

            self.game.add_player(player)

        #print ( "Server succesfully received grid ")

    def tell_distributor(self, distr_port):
        """tell the distributor you exist, and get back list of your peers, and connect with peers"""
        self.distr_port = distr_port

        # create socket for single communication with distributor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # send a message to the distributor
            lat_str = "{:.4f}".format(self.lat)
            lng_str = "{:.4f}".format(self.lng)
            join_mess = 'NEW_SERVER|' + str(self.port) + '|' + str(self.peer_port) + \
                        '|' + lat_str + ';' + lng_str
            send_mess = (join_mess).encode('UTF-8')
            s.connect(('localhost', self.distr_port))
            s.sendall(send_mess)
            # get a peer server port back from the distributor
            data = s.recv(1024)

        message = data.decode('utf-8')
        if message.startswith('DIST|'):
            dist_mess = message.split("|")
            if len(dist_mess) < 2:
                # ill defined message
                pass
            else:
                # the other parts of the message are his peers ports
                for i in range(1, len(dist_mess)):
                    try:
                        peer_port = int(dist_mess[i])
                        # create a new socket for this peer
                        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        # Connect the socket to the port where the server is listening
                        peer_address = ('localhost', peer_port)
                        print('Peer connecting to {} port {}'.format(*peer_address))
                        peer_socket.connect(peer_address)
                        self.peer_connections.append(peer_socket)

                        if i == len(dist_mess)-1:
                            peer_socket.send(b'getgrid')
                            self.receive_grid(peer_socket)

                    except ValueError:
                        # message was not an integer
                        pass
        # now start listening on the peer ports
        self.start_peer_receiving()


    def create_dragon(self):
        """ Create a dragon on the battlefield and send dragon to other all players. """
        x = random.randint(0,25)
        y = random.randint(0,25)
        dragon = Dragon(str(self.game.ID), x,y, self.game)
        message =  "{};addeddragon;{};{};{};{};{};end".format(time.time(),dragon.ID, dragon.x, dragon.y, dragon.hp, dragon.ap)
        self.tickdata += message.encode("utf-8")
        self.game.add_player(dragon)
        self.dragonlist.append(dragon)
        self.game.ID += 1

    def dragon_moves(self):
        """ Let the server create moves for the dragons. """
        message = ""
        # If dragon has died, remove it from server.
        dragonlist = []
        for dragon in self.dragonlist:
            if dragon.hp > 0:
                dragonlist.append(dragon)
        self.dragonlist = dragonlist

        # Look for player around me
        for dragon in self.dragonlist:
            playerlist = []
            for object in self.game.players.values():
                if isinstance(object, Player) and dragon.get_distance(object) < 5:
                    playerlist.append(object)

            # randomly select one of the players
            if playerlist:
                message += "{};attack;{};{};end".format(time.time(),dragon.ID, random.choice(playerlist).ID)

        return message



    def power_down(self):
        """ Close down the server. """
        for connection in self.connections[1:]:
            connection.close()
        # tell the distributor youre stopping
        # create socket for single communication with distributor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # send a message to the distributor
            send_mess = ('OUT_SERVER|' + str(self.port)).encode('UTF-8')
            try:
                s.connect(('localhost', self.distr_port))
                s.sendall(send_mess)
            except ConnectionRefusedError:
                pass

    def peer_power_down(self):
        """close peer connections. """
        for peer_connection in self.peer_connections[1:]:
            try:
                peer_connection.shutdown(socket.SHUT_WR)
            except OSError:
                print("Peer socket already closed.")

    def broadcast_clients(self, data):
        """ Broadcast the message from 1 client to other clients"""
        # Send data to other clients
        for clients in self.connections[1:]:
            clients.sendall(data)

    def broadcast_servers(self, data):
        """ Broadcast the message to other servers"""
        # Send data to other clients
        for server in self.peer_connections[1:]:
            try:
                server.sendall(data)
            except ConnectionResetError:
                print("This peer got removed ", str(server))
            except BrokenPipeError:
                print("This peer game ended ", str(server))

    def send_grid(self, client, theirplayerID):
        """Send the grid to new players or new server"""

        for player in self.game.players.values():
            if player.ID == theirplayerID:
                data = "{};{};{};{};{};{};".format("Myplayer", player.ID, player.x, player.y, player.hp, player.ap)
            else:
                data = "{};{};{};{};{};{};".format( player.type, player.ID, player.x, player.y, player.hp, player.ap)
            client.sendall(data.encode('utf-8'))
        # Send ending character
        client.sendall(b"end")
        #print("finished sending grid")

    def send_grid_server(self, server):
        """Send the grid to a new server"""

        for player in self.game.players.values():
            data = "{};{};{};{};{};{};".format( player.type, player.ID, player.x, player.y, player.hp, player.ap)
            server.sendall(data.encode('utf-8'))
        # Send ending character
        server.sendall(b"end")
        #print("finished sending grid to SERVER")

    def create_player(self, client):
        """Create a player and message this to every body else."""
        # Make sure that new player doesn't spawn on old player
        while True:
            x = random.randint(0,25)
            y = random.randint(0,25)
            if self.game.map[y][x] == "*":
                break

        player = Player(str(self.game.ID), x, y, self.game)
        self.ID_connection[client] = player
        self.game.ID += 1
        self.game.add_player(player)
        self.send_grid(client, player.ID)

        # Send data to other clients
        message =  "{};join;{};{};{};{};{};end".format(time.time(),player.ID, player.x, player.y, player.hp, player.ap)
        self.tickdata += message.encode("utf-8")

    def remove_client(self, client):
        """ Removing client if disconnection happens"""
        player = self.ID_connection[client]
        playerID = player.ID

        if player.hp > 0:
            #self.game.remove_player(player)
            message = "{};leave;{};end".format(time.time(), playerID)
            self.tickdata += message.encode("utf-8")

        self.connections.remove(client)
        print("connection closed")

    def remove_peer(self, peer):
        """ Removing peer if shutdown happens"""
        self.peer_connections.remove(peer)
        print("Peer connection closed")


    def read_ports(self):
        """ Read the sockets for new connections or player noticeses."""
        log = self.log

        self.time_out = self.check_alive
        # Game ticks at whole seconds

        game_ended = False
        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)*self.speedup):
            try:
                # Wait for a connection, based on actual seconds
                # dont sync on whole seconds, but whole second/speedup
                self.time_out = int(time.time()*self.speedup) + 1 - time.time()*self.speedup
                readable, writable, errored = select.select(self.connections, [], [], self.time_out/self.speedup)

                # check for a game end scenario, where either all players or dragons are dead
                if self.game_started:
                    client_total = 0
                    dragon_total = 0
                    for object in self.game.players.values():
                        if isinstance(object, Player):
                            client_total += 1
                        elif isinstance(object, Dragon):
                            dragon_total += 1
                    # make sure you havent ended the game already
                    if not game_ended:
                        # if either is 0, send message to peers and set life time to 10
                        # 10 means sending the message 10 more times, then shut down
                        if client_total == 0:
                            print("DRAGONS WIN THE GAME")
                            log.write("WIN DRAGONS" + '\n')
                            self.life_time = 10
                            self.broadcast_servers(b'WIN DRAGONS')
                            game_ended = True
                        elif dragon_total == 0:
                            print("PLAYERS WIN THE GAME")
                            log.write("WIN PLAYERS" + '\n')
                            self.life_time = 10
                            self.broadcast_servers(b'WIN PLAYERS')
                            game_ended = True
                    print("Clients:", client_total, "Dragons:", dragon_total)

                # update the peer connections for the main process
                while not self.peer_queue.empty():
                    data = self.peer_queue.get()
                    if data[0] == 'getgrid':
                        self.send_grid_server(data[1])
                        self.peer_queue.task_done()
                    # make sure you havent ended the game already
                    elif not game_ended:
                        if (data == b'WIN PLAYERS'):
                            print("PLAYERS WIN THE GAME (told by other server)")
                            log.write("WIN PLAYERS" + '\n')
                            self.life_time = 10
                            game_ended = True
                        elif (data == b'WIN DRAGONS'):
                            print("DRAGONS WIN THE GAME (told by other server)")
                            log.write("WIN DRAGONS" + '\n')
                            self.life_time = 10
                            game_ended = True
                    else:
                        peer_connection = data[0]
                        if peer_connection not in self.peer_connections:
                            self.peer_connections.append(peer_connection)
                        self.peer_queue.task_done()

                if not readable and not writable and not errored:
                    # timeout is reached, just send player total to the distributor
                    # create socket for single communication with distributor
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        # send a message to the distributor
                        send_mess = ('SERVER|' + str(self.port) + '|' + str(len(self.connections)-1)).encode('UTF-8')
                        try:
                            s.connect(('localhost', self.distr_port))
                            s.sendall(send_mess)
                        except ConnectionRefusedError:
                            pass
                    print("No message received")


                    # Make some dragon moves.
                    dragon_data = self.dragon_moves()
                    if dragon_data:
                        self.tickdata += (dragon_data).encode('utf-8')

                    # Always send a message, just send test message if nothing need to ben synced.
                    if self.tickdata:
                        self.broadcast_servers(self.tickdata)
                    else:
                        self.broadcast_servers(b"test")


                    # Change to num_server - 1
                    server_count = 1 # Own peer also in list
                    while not server_count == len(self.peer_connections):
                        try:
                            data = self.server_queue.get(block=True, timeout=0.1/self.speedup)
                            if data == b'test':
                                pass
                            else:
                                self.tickdata += data
                            self.server_queue.task_done()
                        except Empty:
                            print("Late response from peer")
                        server_count += 1

                    # Sort the data
                    data = self.tickdata.decode('utf-8')
                    if data:
                        data = data.split("end")[:-1] # Last end will give a empty index

                        # Parse data
                        data = sorted(data, key=lambda x: float(x.partition(';')[0]))

                        senddata = []
                        for command in data:
                            if self.game.update_grid(command):
                                senddata.append(command)
                                log.write(command + '\n')
                            else:
                                log.write("invalid update" + '\n')

                        # Send to clients
                        data = 'end'.join(senddata) + "endupdate"
                        #print("Data that will be broadcasted: ", data)
                        self.broadcast_clients(data.encode('utf-8'))

                    # Some other handling stuff
                    self.tickdata = b''
                    #print("Finished sending my grid to other servers.")

                else:
                    # got a message
                    for client in readable:
                        # If server side, then new connection
                        if client is self.sock:
                            connection, client_address = self.sock.accept()
                            self.create_player(connection)
                            self.connections.append(connection)
                            # start the game if this is the first player to join
                            if not self.game_started:
                                self.game_started = True
                        # Else we have some data
                        else:
                            try:
                                data = client.recv(64)
                                #print("SERVER RECEIVED", data)
                                if data:
                                    self.tickdata += ((str(time.time())+';').encode('utf-8') + data)
                                else: #connection has closed
                                    self.remove_client(client)
                            except ConnectionResetError:
                                pass


            # Handling stopping servers and closing connections.
            except KeyboardInterrupt:
                self.power_down()
                break

        # always power down for right now
        print("Server shutting down")
        log.close()
        self.power_down()

    def start_peer_receiving(self):
        """Thread for doing moves + send moves"""
        Thread(target=self.read_peer_ports, daemon = True).start()

    def read_peer_ports(self):
        """ Read the sockets for new peer connections or peer game updates."""

        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)*self.speedup):
            try:
                # Wait for a connection
                readable, writable, errored = select.select(self.peer_connections, [], [], self.check_alive/self.speedup)
                if not readable and not writable and not errored:
                    # timeout is reached
                    pass

                else:
                    # got a message
                    for peer in readable:
                        # If server side, then new peer connection
                        if peer is self.peer_sock:
                            connection, peer_address = self.peer_sock.accept()
                            print ("Peer connected from {}".format(peer_address))
                            if connection not in self.peer_connections:
                                self.peer_connections.append(connection)
                            new_peer_message = "NEW_PEER|" + str()
                            self.peer_queue.put((connection,))
                        # Else we have some data from a peer
                        else:
                            try:
                                data = peer.recv(1028)
                                if data == b'getgrid':
                                    self.peer_queue.put(('getgrid', peer))
                                    continue
                                if (data.decode('utf-8').startswith('WIN PLAYERS')) or (data.decode('utf-8').startswith('WIN DRAGONS')):
                                    self.life_time = 0
                                if data:
                                    # Putting data in queue so it can be read by server
                                    #print(self.peer_port, " received ", data)
                                    self.server_queue.put(data)
                                else: #connection has closed
                                    self.remove_peer(peer)
                            except ConnectionResetError:
                                self.remove_peer(peer)

            # Handling stopping servers and closing connections.
            except KeyboardInterrupt:
                self.power_down()
                break

        # always power down for right now
        print("Peer server shutting down")
        time.sleep(1/self.speedup)
        self.peer_power_down()


if __name__ == '__main__':
    import sys
    client_port = int(sys.argv[1])
    peer_port = int(sys.argv[2])
    distr_port = int(sys.argv[3])
    run_time = int(sys.argv[4])
    check_alive = int(sys.argv[5])
    server_id = int(sys.argv[6])
    lat = int(sys.argv[7])
    lng = int(sys.argv[8])
    num_dragons = int(sys.argv[9])

    # Setup a new server
    s = Server(port=client_port, peer_port=peer_port, life_time=run_time, check_alive=check_alive,
        ID=server_id, lat=lat, lng=lng, num_dragons=num_dragons)
    print("Created server process " + str(client_port))
    # tell the distributor you exist
    s.tell_distributor(distr_port)
    # let the server handle all incoming messages
    s.read_ports()
    print("Server closed on port " + str(client_port))
