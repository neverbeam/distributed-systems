import socket
import select
import random
import time

class gridobject:
    """ Defines a grid object on the grid. Could be player or dragon"""
    def __init__(self, name):
        self.x = random.randint(0,25)
        self.y = random.randint(0,25)
        self.hp = 10
        self.ap = 5
        self.cd = 0
        self.name = name


class Server:
    def __init__(self, port=10000):
        self.start_up(port)
        # we could also place object on a 25x25 grid
        self.grid = {}

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
        for connection in self.connections:
            connection.close()

    def update_grid(self, data):
        """Update my grid and pass on the message"""
        # Requires server parsing here
        for clients in self.connections[1:]:
            clients.sendall(data)

    def send_grid(self, client):
        """Send the grid to new players"""

        for player in self.grid.values():
            data = "{};{};{};{};{};".format(player.name, player.x, player.y, player.hp, player.ap)
            client.sendall(data.encode('utf-8'))
        # Send ending character
        client.sendall(b"end")
        print("finished sending grid")

    def create_player(self, client):
        """Create a player and message this to every body else."""
        player = gridobject(len(self.grid))
        self.grid[client] = player
        self.send_grid(client)

        # Send data to other clients
        data = "join;{};{};{};{};{}".format(player.name, player.x, player.y, player.hp, player.ap)
        for clients in self.connections[1:]:
            clients.sendall(data.encode('utf-8'))


    def read_ports(self):
        """ Read the sockets for new connections or player noticeses."""
        while True:
            try:
                # Wait for a connection
                readable, writable, errored = select.select(self.connections, [], [])

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
                        print('received {!r}'.format(data))
                        if data:
                            update = self.update_grid(data) # perhaps do this in another thread
                        else: #connection has closed
                            print ("closing the connection")
                            self.connections.remove(client)
            # Handling stopping servers and closing connections.
            except KeyboardInterrupt:
                self.power_down()


if __name__ == '__main__':
    s = Server()
    s.read_ports()


# Receive update  ->  update -> send back -> handle new connection
