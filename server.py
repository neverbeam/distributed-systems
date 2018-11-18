import socket
import select

class Server:
    def __init__(self, port=10000):
        self.start_up(port)

    def start_up(self, port=10000):
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
        print ("Terminating and closing existing connections")
        for connection in self.connections:
            connection.close()

    def update_grid(self, data):
        # placeholder
        print ("updated")

    def read_ports(self):
        while True:
            try:
                # Wait for a connection
                print('waiting for a connection')
                readable, writable, errored = select.select(self.connections, [], [])

                for client in readable:
                    # If server side, then new connection
                    if client is self.sock:
                        connection, client_address = self.sock.accept()
                        self.connections.append(connection)
                        print ("Someone connected from {}".format(client_address))
                    # Else we have some data
                    else:
                        data = client.recv(64)
                        print('received {!r}'.format(data))
                        if data:
                            print('sending data back to the client')
                            update = self.update_grid(data) # perhaps do this in another thread
                            client.sendall(data)  # Perhaps do a broadcast here.
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
