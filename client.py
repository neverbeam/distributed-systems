import socket
import select
from threading import Thread


class gridobject:
    def __init__(self, data):
        self.name = data[0]
        self.x = int(data[1])
        self.y = int(data[2])
        self.hp = int(data[3])
        self.ap = int(data[4])

        print ("made player with: \n name:{} \n x: {} \n y:{} \n hp: {} \n ap: {}".format(self.name, self.x, self.y, self.hp, self.ap))


class Client:
    def __init__(self, port=10000):
        self.sock = self.connect_server(port=port)

    def recieve_grid(self, sock):
        """ Receive the current state of the grid from the server. """
        self.grid = {}
        data = ""
        # Keep receiving until an end has been send. TCP gives in order arrival
        while True:
            data += sock.recv(128).decode('utf-8')
            if data[-3:] == "end":
                break

        #Parse the data so that the user contains the whole grid.
        data = data.split(";")
        del data[-1]
        for i in range(0, len(data), 5):
            playerdata = data[i:i+5]
            player = gridobject(playerdata)
            self.grid[player.name] = player

        print ( "succesfully received grid")


    def connect_server(self, port=10000):
        """ Connect to the server. """
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', port)
        print('connecting to {} port {}'.format(*server_address))
        sock.connect(server_address)
        self.recieve_grid(sock)

        return sock

    def disconnect_server(self):
        """ disconnect from the server"""
        # close the socket
        self.sock.close()

    def send_message(self, message):
        """ Send an message/action to the server"""
        # Send data
        print('sending {!r}'.format(message))
        self.sock.sendall(message.encode('utf-8'))

    def start_moving(self):
        """Thread for doing moves + send moves"""
        Thread(target=self.player_moves, args=()).start()

    def player_moves(self):
        """ User input function. """
        while True:
            # message input action;player;argument
            message = input("Create an action:\n")
            self.update_grid(message)
            self.send_message(message)

    def update_grid(self, data):
        """ Update my grid. """
        data = data.split(';')

        if data[0] == "join":
            player = gridobject(data[1:])
            self.grid[player.name] = player
        elif data[0] == "move":
            player = self.grid[data[1]]
            player.x = int(data[2])
            player.y = int(data[3])



    def server_input(self):
        """ Check for server input. """
        while True:
            readable, writable, errored = select.select([self.sock], [self.sock], [])
            data = self.sock.recv(64)
            if data:
                # update my update_grid
                self.update_grid(data.decode('utf-8'))
                print ("message: " + data.decode('utf-8'))



if __name__ == "__main__":
    # Connect to the host
    c = Client() # perhaps argument port

    c.start_moving()

    # Receive input from servers
    c.server_input()

    print('closing socket') # probably requires try except keyboard interrupt
    c.disconnect_server()
