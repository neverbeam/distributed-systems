import socket
import select
import random
import time
from Game import *
from queue import Queue
from threading import Thread



class Server:
    def __init__(self, port=10000, peer_port=10100, life_time=None, check_alive=1, ID=0):
        # we could also place object on a 25x25 grid
        self.port = port
        self.peer_port = peer_port
        self.life_time = life_time
        self.start_time = time.time()
        self.check_alive = check_alive
        self.game = Game(self, ID,2,1)
        self.ID_connection = {}
        self.queue = Queue()
        self.server_queue = Queue()
        self.peer_queue = Queue()
        self.start_up(port, peer_port)


    def start_up(self, port=10000, peer_port=10100):
        """ Create an server for das game. """
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', port)
        print('Server starting up on {} port {}'.format(*server_address))
        self.sock.bind(server_address)
        self.connections = [self.sock]

        self.dragonlist = []
        self.create_dragon()

        # Listen for incoming connections
        self.sock.listen(3)


        # FOR PEERS
        # Create a TCP/IP socket
        self.peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_peer_address = ('localhost', peer_port)
        print('Peer server starting up on {} port {}'.format(*server_peer_address))
        self.peer_sock.bind(server_peer_address)
        self.peer_connections = [self.peer_sock]

        # Listen for incoming connections
        self.peer_sock.listen(4)

    # tell the distributor you exist, and get back list of your peers, and connect with peers
    def tell_distributor(self, distr_port):
        self.distr_port = distr_port

        # create socket for single communication with distributor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # send a message to the distributor
            send_mess = ('NEW_SERVER|' + str(self.port) + '|' + str(self.peer_port)).encode('UTF-8')
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
            elif dist_mess[1] == 'NO_PEERS':
                # TODO you have to initialize the grid, because no peers yet
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
                        # TODO NOW: this does not work because the peer_address is not yet added to this socket?
                        peer_socket.connect(peer_address)
                        self.peer_connections.append(peer_socket)
                        # TODO get the game from the last added peer
                        if i == len(dist_mess)-1:
                            pass

                    except ValueError:
                        # message was not an integer
                        pass
        # now start listening on the peer ports
        self.start_peer_receiving()

    def create_dragon(self):
        dragon = Dragon(str(self.game.ID), 15,15, self.game)
        self.game.ID += 1
        self.game.add_player(dragon)
        self.dragonlist.append(dragon)
        Thread(target=self.run_dragon, args=(self.queue,), daemon = True).start()

    def run_dragon(self, queue):
        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)):
            time.sleep(2)
            # Look for player around me
            for dragon in self.dragonlist:
                playerlist = []
                for object in self.game.players.values():
                    if isinstance(object, Player) and dragon.get_distance(object) < 5:
                        playerlist.append(object)

                # randomly select one of the players
                if playerlist:
                    message = "attack;{};{};".format(dragon.ID, random.choice(playerlist).ID)
                    queue.put(message)



    def power_down(self):
        """ Close down the server. """
        for connection in self.connections[1:]:
            connection.close()
        # tell the distributor youre stopping
        # create socket for single communication with distributor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # send a message to the distributor
            send_mess = ('OUT_SERVER|' + str(self.port)).encode('UTF-8')
            s.connect(('localhost', self.distr_port))
            s.sendall(send_mess)

    def peer_power_down(self):
        # close peer connections
        for peer_connection in self.peer_connections[1:]:
            peer_connection.shutdown(socket.SHUT_WR)

    def broadcast_clients(self, data):
        """ Broadcast the message from 1 client to other clients"""
        # Send data to other clients
        for clients in self.connections[1:]:
            clients.sendall(data)

    def broadcast_servers(self, data):
        """ Broadcast the message to other servers"""
        # Send data to other clients
        for server in self.peer_connections[1:]:
            server.sendall(data)

    def send_grid(self, client):
        """Send the grid to new players or new server"""

        for player in self.game.players.values():
            data = "{};{};{};{};{};{};".format( player.type, player.ID, player.x, player.y, player.hp, player.ap)
            client.sendall(data.encode('utf-8'))
        # Send ending character
        client.sendall(b"end")
        print("finished sending grid")

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
        self.send_grid(client)

        # Send data to other clients
        data = "join;{};{};{};{};{};".format(player.ID, player.x, player.y, player.hp, player.ap)
        self.broadcast_clients(data.encode('utf-8'))

    def remove_client(self, client, log):
        """ Removing client if disconnection happens"""
        player = self.ID_connection[client]
        playerID = player.ID
        message = "leave;{};".format(playerID)

        if player.hp > 0:
            self.game.remove_player(player)
            self.broadcast_clients(message.encode('utf-8'))

        log.write(message + "\n")
        self.connections.remove(client)
        print("connection closed")

    def remove_peer(self, peer):
        """ Removing peer if shutdown happens"""
        #log.write("A peer left")
        self.peer_connections.remove(peer)
        print("Peer connection closed")



    def read_ports(self):
        """ Read the sockets for new connections or player noticeses."""
        log = open('logfile','w')

        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)):
            try:
                # Wait for a connection
                readable, writable, errored = select.select(self.connections, [], [], self.check_alive)

                # See if a dragon move needs to be made.
                while not self.queue.empty():
                    data = self.queue.get()
                    self.game.update_grid(data)
                    self.broadcast_clients(data.encode('utf-8'))
                    self.queue.task_done()
                    log.write(data)

                # Check whether there are message from other servers
                while not self.server_queue.empty():
                    data = self.server_queue.get()
                    data = data.decode('utf-8')
                    self.game.update_grid(data)
                    # TODO use the timestamp of this message to synchronise moves
                    # self.broadcast_servers(data.encode('utf-8'))
                    self.server_queue.task_done()
                    log.write(data)

                # update the peer connections for the main process
                while not self.peer_queue.empty():
                    peer_connection = self.peer_queue.get()
                    if peer_connection not in self.peer_connections:
                        self.peer_connections.append(peer_connection)
                    self.peer_queue.task_done()

                if not readable and not writable and not errored:
                    # timeout is reached, just send player total to the distributor
                    # create socket for single communication with distributor
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        # send a message to the distributor
                        send_mess = ('SERVER|' + str(len(self.connections)-1)).encode('UTF-8')
                        s.connect(('localhost', self.distr_port))
                        s.sendall(send_mess)
                    print("No message received")

                else:
                    # got a message
                    for client in readable:
                        # If server side, then new connection
                        if client is self.sock:
                            connection, client_address = self.sock.accept()
                            print ("Someone connected from {}".format(client_address))
                            log.write("Someone connected from {}\n".format(client_address))
                            self.create_player(connection)
                            self.connections.append(connection)
                        # Else we have some data
                        else:
                            data = client.recv(64)
                            print("SERVER RECEIVED", data)
                            if data:
                                # Check whether update grid was succesfull
                                if self.game.update_grid(data.decode('utf-8')):
                                    self.broadcast_clients(data)
                                    #print ("TRYOUUTTT0", data, data+b"end of move" )
                                    self.broadcast_servers(data)
                                    log.write(data.decode('utf-8') + "\n")
                            else: #connection has closed
                                self.remove_client(client, log)
            # Handling stopping servers and closing connections.
            except KeyboardInterrupt:
                # self.power_down()
                break

        # always power down for right now
        print("Server shutting down")
        log.close()
        self.power_down()



    # TODO THIS
    def start_peer_receiving(self):
        """Thread for doing moves + send moves"""
        Thread(target=self.read_peer_ports, daemon = True).start()

    def read_peer_ports(self):
        """ Read the sockets for new peer connections or peer game updates."""
        log = open('logfile','w')

        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)):
            try:
                # Wait for a connection
                readable, writable, errored = select.select(self.peer_connections, [], [], self.check_alive)
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
                            self.peer_queue.put(connection)
                        # Else we have some data from a peer
                        else:
                            data = peer.recv(64)
                            if data:
                                # PUtting data in queue so it can be read by server
                                print(self.peer_port, " received ", data)
                                self.server_queue.put(data)
                            else: #connection has closed
                                self.remove_peer(peer)

            # Handling stopping servers and closing connections.
            except KeyboardInterrupt:
                # self.power_down()
                break

        # always power down for right now
        print("Peer server shutting down")
        log.close()
        self.peer_power_down()


if __name__ == '__main__':
    import sys
    client_port = int(sys.argv[1])
    peer_port = int(sys.argv[2])
    distr_port = int(sys.argv[3])
    run_time = int(sys.argv[4])
    check_alive = int(sys.argv[5])

    # Setup a new server
    s = Server(port=client_port, peer_port=peer_port, life_time=run_time, check_alive=check_alive)
    print("Created server process " + str(client_port))
    # tell the distributor you exist
    s.tell_distributor(distr_port)
    # let the server handle all incoming messages
    s.read_ports()
    print("Server closed on port " + str(client_port))
