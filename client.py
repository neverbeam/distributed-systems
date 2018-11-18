import socket
import select
from threading import Thread


class Client:
    def __init__(self, port=10000):
        self.sock = self.connect_server(port=port)

    def connect_server(self, port=10000):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('localhost', port)
        print('connecting to {} port {}'.format(*server_address))
        sock.connect(server_address)

        return sock

    def disconnect_server(self):
        # close the socket
        self.sock.close()

    def send_message(self, message):
        # Send data
        print('sending {!r}'.format(message))
        self.sock.sendall(message)

    def start_moving(self):
        # Thread for doing moves + send moves
        Thread(target=self.player_moves, args=()).start()

    def player_moves(self):
        message = b'This is the message.  It will be repeated.'
        self.send_message(message)

    def server_input(self):
        while True:
            readable, writable, errored = select.select([self.sock], [self.sock], [])
            data = self.sock.recv(64)
            if data:
                # update my update_grid
                print ("updating grid")



if __name__ == "__main__":
    # Connect to the host
    c = Client() # perhaps argument port

    c.start_moving()

    # Receive input from servers
    c.server_input()

    print('closing socket')
    c.disconnect_server()
