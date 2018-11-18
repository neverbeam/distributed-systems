# import subprocess
# import os

# if __name__ == '__main__':
#   # get path to current running file
#   path_to_here = os.path.dirname(os.path.abspath( __file__ )) + '/'
#   # subprocess.call('python client.py', shell=True)
#   subprocess.call('python3 ' + path_to_here + 'client.py')

import multiprocessing as mp
from client import Client
import time

# give the client and a queue to write to
def client_process(q):
    # Connect to the host
    c = Client() # perhaps argument port
    c.start_moving()
    # Receive input from servers
    c.server_input()
    print('closing socket')
    c.disconnect_server()

if __name__ == '__main__':
    mp.set_start_method('spawn')

    q = mp.Queue()
    p1 = mp.Process(target=client_process, args=(q,))

    # spawn a process
    p1.start()
    # print(q.get())
    # print(q.get())

    # spawn another process
    time.sleep(1)
    p2 = mp.Process(target=client_process, args=(q,))
    p2.start()

    # wait until the process terminates
    p1.join()
    p2.join()
