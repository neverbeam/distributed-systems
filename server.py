import socket
import select
import random
import time
from Game import *

class Server:
    def __init__(self, port=10000, life_time=None, check_alive=1):
        self.start_up(port)
        # we could also place object on a 25x25 grid
        self.life_time = life_time
        self.start_time = time.time()
        self.check_alive = check_alive
        self.game = Game(self, 1,2,1)
        self.ID_connection = {}


    def start_up(self, port=10000):
        """ Create an server for das game. """
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', port)
        print('starting up on {} port {}'.format(*server_address))
        self.sock.bind(server_address)
        self.connections = [self.sock]

        # Listen for incoming connections, # incomming connections
        self.sock.listen(3)

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
            x = random.randint(0,24)
            y = random.randint(0,24)
            if self.game.map[y][x] == "*":
                break

        player = Player(self.game.ID, x, y, self.game)
        self.ID_connection[client] = player
        self.game.ID += 1
        self.game.add_player(player)
        self.send_grid(client)

        # Send data to other clients
        data = "join;{};{};{};{};{}".format(player.ID, player.x, player.y, player.hp, player.ap)
        for clients in self.connections[1:]:
            clients.sendall(data.encode('utf-8'))

    def remove_client(self, client):
        """ Removing client if disconnection happens"""
        player = self.ID_connection[client]
        self.game.remove_player(player)
        self.connections.remove(client)
        print("connection closed")

    def read_ports(self):
        """ Read the sockets for new connections or player noticeses."""
        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)):
            try:
                # Wait for a connection
                readable, writable, errored = select.select(self.connections, [], [], self.check_alive)
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
                            self.create_player(connection)
                            self.connections.append(connection)
                        # Else we have some data
                        else:
                            data = client.recv(64)
                            print(data)
                            if data:
                                update = self.game.update_grid(data.decode('utf-8').split(";")
)
                                self.broadcast_clients(data)
                            else: #connection has closed
                                self.remove_client(client)
            # Handling stopping servers and closing connections.
            except KeyboardInterrupt:
                # self.power_down()
                break

        # always power down for right now
        print("Server shutting down")
        self.power_down()


if __name__ == '__main__':
    s = Server()
    s.read_ports()


# Receive update  ->  update -> send back -> handle new connection
