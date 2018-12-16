import socket
import select
import time
from threading import Thread
from queue import Queue
import Game
from Player import *
import numpy as np

class Client:
    def __init__(self, distr_port=11000, demo=False, life_time=1000):
        self.demo = demo
        self.life_time = life_time
        self.start_time = time.time()
        self.keep_alive = True
        server_port = self.get_server(distr_port)
        self.sock = self.connect_server(port=server_port)
        self.queue = Queue()

    def receive_grid(self, sock):
        """ Receive the current state of the grid from the server. """
        self.game = Game.Game(self)
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
        highestID = 0
        for i in range(0, len(data), 6):
            playerdata = data[i:i+6]
            if playerdata[0] == "Player":
                player = Player(playerdata[1], int(playerdata[2]), int(playerdata[3]) ,self.game)
                player.hp = int(playerdata[4])
                player.ap = int(playerdata[5])

                # The highest id is the new player, so me
                if int(playerdata[1]) > highestID:
                    highestID = int(playerdata[1])
            elif playerdata[0] == "Dragon":
                print("found a dragon")
                player = Dragon(playerdata[1], int(playerdata[2]), int(playerdata[3]) ,self.game)
                player.hp = int(playerdata[4])
                player.ap = int(playerdata[5])

            self.game.add_player(player)

        self.myplayer = self.game.players[str(highestID)]
        print ( "succesfully received grid")


    # talk to the distributor to get a server port to connect to
    def get_server(self, distr_port=11000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # send a message to the distributor
            s.connect(('localhost', distr_port))
            s.sendall(b'CLIENT|')
            # get a server port back from the distributor
            data = s.recv(1024)
            message = data.decode('utf-8')
            if message.startswith('DIST|'):
                dist_mess = message.split("|")
                if len(dist_mess) < 2 or len(dist_mess) > 2:
                    # ill defined message
                    pass
                else:
                    try:
                        server_port = int(dist_mess[1])
                        return server_port
                    except ValueError:
                        # message was not an integer
                        pass
        # distributor did not respond, should not happen
        print("ERROR: no distributor response")
        return 0

    def connect_server(self, port=10000):
        """ Connect to the server. """
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', port)
        print('Client connecting to {} port {}'.format(*server_address))
        sock.connect(server_address)
        self.receive_grid(sock)

        return sock

    def disconnect_server(self):
        """ disconnect from the server"""
        # close the socket
        self.sock.shutdown(socket.SHUT_WR)

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
                if data.split(";")[1] != self.myplayer.ID:
                    print( "data from thread:", data)
                    self.game.update_grid(data)
                    # do something with row
                    self.queue.task_done()

            message = ""
            if self.demo:
                # Get a message from an actual human running the demo program
                # THIS BLOCKS OTHER INPUT NOW!!
                message = input("Create an action:\n")
            else:
                # check if the player should disconnect based on playtime
                if self.life_time < (time.time() - self.start_time):
                    # Let the server know you want to disconnect
                    print ("DISCONNECTING", self.myplayer.ID, "-----------------------------------------------------")
                    self.keep_alive = 0
                    continue

                else:
                    # This message should be created by an automated system (computer that plays game)
                    time.sleep(1)
                    # NORMAL BEHAVIOR IS GOING TO BE HERE
                    # NOrmal order -> look for heals -> look for attacks -> MOve
                    # Look for heals in space around me
                    playerlist = []
                    dragonlist = []
                    for object in self.game.players.values():
                        if isinstance(object, Player) and self.myplayer.get_distance(object) < 5:
                            playerlist.append(object)
                        elif isinstance(object, Dragon):
                            dragonlist.append(object)

                    if not dragonlist:
                        self.keep_alive = 0

                    for player in playerlist:
                        if player.hp < 0.5*player.max_hp and player != self.myplayer:
                            message = "heal;{};{}".format(self.myplayer.ID, player.ID)
                            break

                    # Message unchanged , no healing done
                    if message == "":
                        for dragon in dragonlist:
                            if self.myplayer.get_distance(dragon)<3:
                                message = "attack;{};{};".format(self.myplayer.ID, dragon.ID)
                                break
                    # message unchanged, no dragon in place
                    if message == "":
                        # Find the closest dragon
                        min_dragon_distance = 30
                        for dragon in dragonlist:
                            if self.myplayer.get_distance(dragon) < min_dragon_distance:
                                min_dragon_distance = self.myplayer.get_distance(dragon)
                                min_dragon = dragon

                        # move to this dragon.
                        directions = []
                        if (min_dragon.x-self.myplayer.x)<0:
                            directions.append("left")
                        elif (min_dragon.x-self.myplayer.x)>0:
                            directions.append("right")
                        elif (min_dragon.y-self.myplayer.y)<0:
                            directions.append("down")
                        elif (min_dragon.y-self.myplayer.y)>0:
                            directions.append("up")
                        message = "move;{};{};".format(self.myplayer.ID, np.random.choice(directions)) ### What TODO if move is invalid?

                    #message = "Debug message;, time=" + str(time.time() - self.start_time)
            if self.game.update_grid(message):
                self.send_message(message)

        self.disconnect_server()

    def server_input(self, queue):
        """ Check for server input. """
        while (self.life_time == None) or (self.life_time > (time.time() - self.start_time)):
            readable, writable, errored = select.select([self.sock], [], [])

            data = self.sock.recv(64)
            if data:
                # update my update_grid
                queue.put(data)
                print ("message: incomming " + data.decode('utf-8'))



if __name__ == "__main__":
    import sys
    distr_port = int(sys.argv[1])
    play_time = int(sys.argv[2])

    # Connect to the host
    c = Client(distr_port=distr_port, demo=False, life_time=play_time)
    print("Created client process")
    # Receive input from servers
    c.start_receiving()
    # let the client do moves until its playtime is up
    c.player_moves()

    # remove the player from the server
    c.disconnect_server()
    time.sleep(2) #Need a timing here, to prevent too quick shutdown
    print("Closing client process connected to server on port ") #+str(c.port))
