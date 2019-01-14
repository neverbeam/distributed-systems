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
import os
import sys


class Populator:
    def __init__(self, manual=False, experiment_num=0, experiment_arg=1):
        mp.set_start_method('spawn')
        self.commands = self.list_commands()
        self.keep_alive = True
        self.servers = {}
        self.clients = {}
        self.speedup = 1.0
        self.printing = False

        if manual:
            self.get_input()
        else:
            if experiment_num == 1:
                self.test_setup_2s_2c()
            elif experiment_num == 2:
                self.wow_setup()
            elif experiment_num == 3:
                self.test_setup_geo(experiment_arg, 100)
            elif experiment_num == 4:
                self.test_setup_max()

    # creates a running client
    def client_process(self, distr_port, play_time, lat, lng, demo=False):
        # Connect to the host
        c = Client(distr_port=distr_port, demo=demo, life_time=play_time, lat=lat, lng=lng, speedup=self.speedup, printing=self.printing)
        print("Created client process")
        if c.joined_game:
            # Receive input from servers
            c.start_receiving()
            # let the client do moves until its playtime is up
            c.player_moves()

            # remove the player from the server
            c.disconnect_server()
            print("Closing client process connected to server on port " + str(c.port))
        else:
            print("No game available")


    # creates a running server
    def server_process(self, client_port, peer_port, distr_port, run_time, check_alive, ID, lat, lng, num_dragons=1):
        # Setup a new server
        s = Server(port=client_port, peer_port=peer_port, life_time=run_time, check_alive=check_alive,
            ID=ID, lat=lat, lng=lng, num_dragons=num_dragons, speedup=self.speedup, printing=self.printing)
        print("Created server process " + str(client_port))
        # tell the distributor you exist
        s.tell_distributor(distr_port)
        # let the server handle all incoming messages
        s.read_ports()
        print("Server closed on port " + str(client_port))


    # creates a running distributor
    def distributor_process(self, listen_port, run_time):
        if not self.printing:
            sys.stdout = open(os.devnull, 'w')
        d = Distributor(port=listen_port, life_time=run_time, speedup=self.speedup, printing=self.printing)
        print("Created distributor process " + str(listen_port))
        # let the distributor listen to all incoming messages until lifetime is up
        d.read_ports()
        print("Distributor closed on port " + str(listen_port))


    # runs a test version that should work (has 2 players and 2 servers)
    def test_setup_2s_2c(self):
        # allow printing to terminal
        self.printing = True
        # set a speedup factor for testing
        self.speedup = 2.0

        # initialize the distributor
        dp = 11000
        d = mp.Process(target=self.distributor_process, args=(dp, 23))
        d.start()
        time.sleep(0.3/self.speedup)

        servers = []
        num_servers = 2
        for i in range(num_servers):
            # run a server
            s = mp.Process(target=self.server_process, args=(10000+i, 10100+i, dp, 20, 1, i*100, 1, 1, 2.3))
            s.start()
            servers.append(s)
            time.sleep(0.1/self.speedup)

        # spawn a client process
        c1 = mp.Process(target=self.client_process, args=(dp, 15, 1, 1))
        c1.start()

        # spawn another client process
        time.sleep(1/self.speedup)
        c2 = mp.Process(target=self.client_process, args=(dp, 10, 1, 1))
        c2.start()

        # wait until the client processes terminate
        c2.join()
        c1.join()
        # then close the servers
        for s in servers:
            s.join()
        # then close the distributor
        d.join()


    # runs a test version pushing the bounds of player/server/player total
    def test_setup_max(self, num_servers=2, num_clients=50, speedup=1.0):
        self.speedup = speedup
        self.printing = True
        # initialize the distributor
        dp = 11000
        d = mp.Process(target=self.distributor_process, args=(dp, 45*self.speedup))
        d.start()
        time.sleep(0.3)

        servers = []
        for i in range(num_servers):
            # run a server
            server_id = i*1000
            s = mp.Process(target=self.server_process, args=(10000+i, 10100+i, dp, 40*self.speedup, 1, server_id, 1, 1, 1))
            s.start()
            servers.append(s)
            time.sleep(0.2)

        time.sleep(0.2)
        clients = []
        for i in range(num_clients):
            # spawn a client process
            c = mp.Process(target=self.client_process, args=(dp, 15*self.speedup, 1, 1))
            c.start()
            clients.append(c)
            time.sleep(0.0)

        # wait until the client processes terminate
        for c in clients:
            c.join()
        # then close the servers
        for s in servers:
            s.join()
        # then close the distributor
        d.join()


    # runs a test version based on geolocations
    def test_setup_geo(self, num_root_servers, num_players):
        # initialize the distributor
        dp = 11000
        # create a distributor that terminates after all servers are done
        d = mp.Process(target=self.distributor_process, args=(dp, num_players*2.7+3))
        d.start()
        time.sleep(0.5)

        # create servers with different geo locations
        servers = []
        space_between_servers = 1./num_root_servers
        for i in range(num_root_servers):
            sx = (i+1) * space_between_servers - space_between_servers/2.
            for j in range(num_root_servers):
                sy = (j+1) * space_between_servers
                # run a server on those latitude longitude
                server_num = (i*num_root_servers)+j
                # create servers that are closed when all players are done
                s = mp.Process(target=self.server_process, args=(10000+server_num, 10100+server_num, dp,
                        num_players*2.5+1, 1, server_num*(num_players+1), sy, sx))
                s.start()
                servers.append(s)

        time.sleep(num_players*0.2)

        # create clients with random geo locations in [1,1]
        clients = []
        for i in range(num_players):
            x = random.random()
            y = random.random()
            # spawn a client process
            c = mp.Process(target=self.client_process, args=(dp, 2, y, x))
            c.start()
            clients.append(c)
            time.sleep(2)

        # wait until the client processes terminate
        for c in clients:
            c.join()
        # then close the servers
        for s in servers:
            s.join()
        # then close the distributor
        d.join()


    # use the game trace to create clients with a given lifespan
    def wow_setup(self):
        # setup for running game trace
        trace_start = time.time()
        sim_time = 900
        join_steps = [0.5, 0.7, 1]
        num_servers = 5
        dragons_per_server = 1
        self.printing = False

        for join_step in join_steps:
            with open("join_step_results.txt", "a") as join_step_results:
                join_step_results.write("--------------\njoin step: "+str(join_step))
            self.speedup = join_step/2
            for n in range(1):
                try: 
                    # create a distributor that terminates after all servers are done
                    dp = 11000
                    d = mp.Process(target=self.distributor_process, args=(dp, sim_time*self.speedup))
                    d.start()
                    time.sleep(0.5)

                    servers = []
                    logfiles = []
                    for i in range(num_servers):
                        # run a server
                        server_id = i*1000
                        s = mp.Process(target=self.server_process, args=(10000+i, 10100+i, dp, (sim_time-5)*self.speedup, 1, server_id, 1, 1, dragons_per_server))
                        s.start()
                        servers.append(s)
                        logfiles.append("logfile"+str(server_id))
                        time.sleep(0.2)

                    # start populating
                    clients = []
                    play_dist = pickle.load( open( "wow_trace.p", "rb" ) )
                    populating = True
                    # keep adding players until end of simulation
                    while (trace_start + (sim_time-10)*self.speedup) > time.time():
                        # get a random lifetime from the wow distribution
                        playtime = play_dist[random.randint(0, len(play_dist)-1)] / 100.0
                        # create the client
                        c = mp.Process(target=self.client_process, args=(dp,playtime*self.speedup,1,1))
                        c.start()
                        clients.append(c)
                        # wait the set amount of time between adding players
                        time.sleep(join_step)

                    # close all still opened server connections
                    for s in servers:
                        s.join()
                    # close all still opened client connections
                    for c in clients:
                        c.join()
                    d.join()
                except OSError:
                    print("Broke off because of to much clients. ")

                time.sleep(10)
                # analyze who won
                all_last_messages = ""
                dragon_win = 0
                player_win = 0
                invalids = 0
                for logfile in logfiles:
                    with open(logfile, 'r') as f:
                        lines = f.read().splitlines()
                        for line in lines:
                            if line == "WIN DRAGONS":
                                dragon_win += 1
                                break
                            elif line == "WIN PLAYERS":
                                player_win += 1
                                break
                            elif line == "invalid update":
                                invalids += 1
                # show who won
                with open("join_rate_results.txt", "a") as join_step_results:
                    if dragon_win == player_win:
                        join_step_results.write("Draw")
                    elif dragon_win > player_win:
                        join_step_results.write("Dragon win")
                    else:
                        join_step_results.write("Player win")
                    join_step_results.write(invalids)



    # DEPRECATED, DOES NOT WORK ANYMORE
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
    import sys
    experiment_num = int(sys.argv[1])
    experiment_arg = 0
    if experiment_num == 3:
        experiment_arg = int(sys.argv[2])
    p = Populator(manual=False, experiment_num=experiment_num, experiment_arg=experiment_arg)
