# import subprocess
# import os

# if __name__ == '__main__':
#   # get path to current running file
#   path_to_here = os.path.dirname(os.path.abspath( __file__ )) + '/'
#   # subprocess.call('python client.py', shell=True)
#   subprocess.call('python3 ' + path_to_here + 'client.py')

import multiprocessing as mp
from distributor import Distributor
from server import Server
from client import Client
import time
import pandas
import random
import matplotlib.pyplot as plt
import numpy as np
import pickle


class Populator:
    def __init__(self, manual=False):
        mp.set_start_method('spawn')
        self.commands = self.list_commands()
        self.keep_alive = True
        self.servers = {}
        self.clients = {}

        if manual:
            self.get_input()
        else:
            #self.wow_setup(1)
            self.test_setup()

    # creates a running client
    def client_process(self, send_port, play_time, demo=False):
        # Connect to the host
        c = Client(port=send_port, demo=demo, life_time=play_time)
        print("Created client process")
        # Receive input from servers
        c.start_receiving()
        # let the client do moves until its playtime is up
        c.player_moves()

        # # right now just kill the client this way
        # # should be done in a function in client tho
        # c.keep_alive = False # does not even work
        c.disconnect_server()
        time.sleep(5) #Need a timing here, to prevent too quick shutdown
        print("Closing client process connected to server on port " + str(c.port))


    # creates a running server
    def server_process(self, listen_port, run_time, check_alive):
        # Setup a new server
        s = Server(port=listen_port, life_time=run_time, check_alive=check_alive)
        print("Created server process")
        # let the server handle all incoming messages
        s.read_ports()
        print("Server closed on port " + str(listen_port))


    # creates a running distributor
    def distributor_process(self, listen_port, run_time):
        d = Distributor(port=listen_port, life_time=run_time)
        print("Created distributor process")
        #TODO this dynamicly by sending messages between server and distributor
        d.add_server(10000)
        # let the distributor listen to all incoming messages until lifetime is up
        d.handle_messages()
        print("Distributor closed on port " + str(listen_port))


    # runs a test version that should work
    def test_setup(self):
        # initialize the distributor
        d = mp.Process(target=self.distributor_process, args=(11000, 40))
        d.start()
        time.sleep(0.1)

        # run a server
        s1 = mp.Process(target=self.server_process, args=(10000,30, 1))
        s1.start()
        time.sleep(0.1)

        # spawn a client process
        c1 = mp.Process(target=self.client_process, args=(10000,15))
        c1.start()

        # spawn another client process
        time.sleep(1)
        c2 = mp.Process(target=self.client_process, args=(10000,10))
        c2.start()

        # wait until the client processes terminate
        c2.join()
        c1.join()
        # then close the server
        s1.join()


    # use the game trace to create clients with a given lifespan
    def wow_setup(self, join_rate=2):
        clients = []
        populating = True
        server_port = 10000
        play_dist = pickle.load( open( "wow_trace.p", "rb" ) )

        # create a server setup
        s1 = mp.Process(target=self.server_process, args=(10000,50, 1))
        s1.start()

        # start populating
        while populating:
            # get a random lifetime from the wow distribution
            playtime = play_dist[random.randint(0, len(play_dist)-1)]
            # create the client
            c = mp.Process(target=self.client_process, args=(server_port,playtime))
            c.start()
            # wait the set amount of time between adding players
            time.sleep(join_rate)
            # TODO some termination thing here
            if len(clients) > 10:
                populating = False

        # close all still opened connections
        for c in clients:
            c.join()
        # close the servers
        s1.join()


    # asks you for input, so that you can create/kill/list servers/clients
    def get_input(self):
        while self.keep_alive:
            print("-----COMMANDS-----")
            for command in self.commands:
                print(command)
            print("------------------")
            nocap_input = input().lower()
            # split on any whitespaces
            args = nocap_input.split()

            if len(args) > 1:
                # check to see if a quantity is given
                quantity = 1
                if len(args) >= 2:
                    try:
                        quantity = int(args[2])
                    except (ValueError, TypeError):
                        print("Not an integer quantity, setting to 1.")

                # handles spawn input
                if args[0] == "spawn":
                    name_i = 1
                    if args[1] == "s":
                        for i in range(quantity):
                            name = None
                            while name == None:
                                try_name = "s" + str(i)
                                if try_name not in self.servers.keys():
                                    name = try_name
                            # create and start the process
                            self.servers[name] = mp.Process(target=self.server_process, args=(10000,))
                            self.servers[name].start()
                            print("Added server: " + name)
                    elif args[1] == "c":
                        for i in range(quantity):
                            name = None
                            while name == None:
                                try_name = "c" + str(i)
                                if try_name not in self.clients.keys():
                                    name = try_name
                            # create and start the process
                            self.clients[name] = mp.Process(target=self.client_process, args=(10000,))
                            self.clients[name].start()
                            print("Added client: " + name)
                    else:
                        print("Pick s or c.")

                # handles killing a given server/client
                elif args[0] == "kill":
                    name = args[1]
                    if name[0] == "s":
                        if name in self.servers:
                            # TODO: actually kill the servers process
                            self.servers.pop(name, None)
                            print("Succesfully terminated: " + name)
                        else:
                            print("Dont recognise this server name")
                    elif name[0] == "c":
                        if name in self.clients:
                            # TODO: actually kill the clients process
                            self.clients.pop(name, None)
                            print("Succesfully terminated: " + name)
                        else:
                            print("Dont recognise this client name")
                    else:
                        print("Pick s or c.")

                else:
                    print("You have unrecognised input")

            elif len(args) > 0:
                # show the lists of servers and clients
                if args[0] == "list":
                    print("Servers:")
                    for name, s_obj in self.servers.items():
                        print("\t" + name + "\t" + str(s_obj))

                    print("Clients:")
                    for name, c_obj in self.clients.items():
                        print("\t" + name + "\t" + str(c_obj))

            else:
                print("Need more arguments")

            print() #empty line for style


    def list_commands(self):
        return [
            "spawn [s/c] [quantity]",
            "kill [s/c + number]",
            "list"
        ]



if __name__ == '__main__':
    # set manual to true if you want to manually create servers and clients
    p = Populator(manual=False)
