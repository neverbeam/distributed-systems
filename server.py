import socket
import select
import random
import time
from Game import *
from queue import Queue
from threading import Thread



class Server:
    def __init__(self, port=10000, life_time=None, check_alive=1):
        # we could also place object on a 25x25 grid
        self.life_time = life_time
        self.start_time = time.time()
        self.check_alive = check_alive
        self.game = Game(self, 1,2,1)
        self.ID_connection = {}
        self.queue = Queue()
        self.start_up(port)



    def start_up(self, port=10000):
        """ Create an server for das game. """
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', port)
        print('starting up on {} port {}'.format(*server_address))
        self.sock.bind(server_address)
        self.connections = [self.sock]

        self.dragonlist = []
        self.create_dragon()

        # Listen for incoming connections, # incomming connections
        self.sock.listen(3)

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
        print ("Terminating and closing existing connections")
        for connection in self.connections[1:]:
            connection.close()


    def broadcast_clients(self, data):
        """ Broadcast the message from 1 client to other clients"""
        # Send data to other clients
        for clients in self.connections[1:]:
            clients.sendall(data)

    def send_grid(self, client):
        """Send the grid to new players"""

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
        for clients in self.connections[1:]:
            clients.sendall(data.encode('utf-8'))

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

                if not readable and not writable and not errored:
                    # timeout is reached
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


if __name__ == '__main__':
    s = Server()
    s.read_ports()


# Receive update  ->  update -> send back -> handle new connection
