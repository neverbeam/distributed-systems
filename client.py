
# socket_echo_client.py

import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)


def sendmessage(message):
        # Send data
        print('sending {!r}'.format(message))
        sock.sendall(message)

        # receive  data
        data = sock.recv(64)
        print('received {!r}'.format(data))

message = b'This is the message.  It will be repeated.'

sendmessage(message)


print('closing socket')
sock.close()
