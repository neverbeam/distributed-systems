
# socket_echo_client.py

import socket
import select
from threading import Thread

def connect():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)

    return sock


def sendmessage(message, sock):
        # Send data
        print('sending {!r}'.format(message))
        sock.sendall(message)


def player_moves(sock):
    message = b'This is the message.  It will be repeated.'
    sendmessage(message, sock)

def server_input(sock):
    while True:
        readable, writable, errored = select.select([sock], [sock], [])
        data = sock.recv(64)
        if data:
            # update my update_grid
            print ("updating grid")




if __name__ == "__main__":
    # Connect to the host
    sock = connect() # perhaps argument port

    # Thread for doing moves + send moves
    Thread(target=player_moves, args = (sock,)).start()

    # Receive input from servers
    server_input(sock)

    print('closing socket')
    sock.close()
