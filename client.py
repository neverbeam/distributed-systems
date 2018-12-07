import socket
import select
import time
from threading import Thread
from queue import Queue
from Game import *

class Client:
    def __init__(self, port=10000, demo=False, life_time=1000):
        self.demo = demo
        self.life_time = life_time
        self.start_time = time.time()
        self.keep_alive = True
        self.sock = self.connect_server(port=port)
        self.queue = Queue()

    def receive_grid(self, sock):
        """ Receive the current state of the grid from the server. """
        self.game = Game(self)
        data = ""
        # Keep receiving until an end has been send. TCP gives in order arrival
        while True:
            data += sock.recv(128).decode('utf-8')
            if data[-3:] == "end":
                break

        #Parse the data so that the user contains the whole grid.

        # type, ID, x, y, hp , ap,
        data = data.split(";")
        del data[-1]
        for i in range(0, len(data), 6):
            playerdata = data[i:i+6]
            if data[0] == "Player":
                player = Player(playerdata[1], int(playerdata[2]), int(playerdata[3]) ,self.game)
                player.hp = int(data[5])
                player.ap = int(data[4])
            elif data[0] == "Dragon":
                player = Dragon(playerdata[1], int(playerdata[2]), int(playerdata[3]) ,self.game)
                player.hp = int(data[5])
                player.ap = int(data[4])

            self.game.add_player(player)

        self.myplayer = player # Is this in order?
        print ( "succesfully received grid")


    def connect_server(self, port=10000):
        """ Connect to the server. """
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', port)
        print('connecting to {} port {}'.format(*server_address))
        sock.connect(server_address)
        self.receive_grid(sock)

        return sock

    def disconnect_server(self):
        """ disconnect from the server"""
        # close the socket
        print('closing socket')
        time.sleep(0.000001) #Need a timing here, to prevent too quick shutdown
        self.sock.close()

    def send_message(self, message):
        """ Send an message/action to the server"""
        # Send data
        print('sending {!r}'.format(message))
        self.sock.sendall(message.encode('utf-8'))

    def start_receiving(self):
        """Thread for doing moves + send moves"""
        Thread(target=self.server_input, args=(self.queue,), daemon = True).start()

    def player_moves(self):
        """ User input function. """
        while self.keep_alive:
            # First process server dataself.
            while not self.queue.empty():
                data = self.queue.get().decode('utf-8')
                print ("given data", data)
                if data.split(";")[1] != self.myplayer.ID:
                    print( "data from thread:", data)
                    self.game.update_grid(data)
                    # do something with row
                    self.queue.task_done()

            # message input action;player;argument
            message = "ERROR: no message"
            if self.demo:
                # Get a message from an actual human running the demo program
                # THIS BLOCKS OTHER INPUT NOW!!
                message = input("Create an action:\n")
            else:
                # check if the player should disconnect based on playtime
                if self.life_time < (time.time() - self.start_time):
                    # Let the server know you want tselfo disconnect
                    message = ("DISCONNECTING PLS")
                    self.keep_alive = False
                    print ("DISONNECTING -----------------------------------------------------")

                else:
                    # This message should be created by an automated system (computer that plays game)
                    time.sleep(2)
                    message = "Debug message, time=" + str(time.time() - self.start_time)
            self.game.update_grid(message)
            self.send_message(message)



    def server_input(self, queue):
        """ Check for server input. """
        while self.keep_alive:
            readable, writable, errored = select.select([self.sock], [], [])

            data = self.sock.recv(64)
            if data:
                # update my update_grid
                queue.put(data)
                print ("message: incomming " + data.decode('utf-8'))



if __name__ == "__main__":
    # Connect to the host
    c = Client(demo=True) # perhaps argument port

    c.start_receiving()

    # Receive input from servers
    c.player_moves()

    print('closing socket') # probably requires try except keyboard interrupt
    c.disconnect_server()
