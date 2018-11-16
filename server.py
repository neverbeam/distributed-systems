# socket_echo_server.py

import socket
import select

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
connections = [sock]

# Listen for incoming connections, # incomming connections
sock.listen(3)

def update_grid(data):
    print ("updated")

while True:
    try:
        # Wait for a connection
        print('waiting for a connection')
        readable, writable, errored = select.select(connections, [], [])

        for s in readable:
            # If server side, then new connection
            if s is sock:
                connection, client_address = sock.accept()
                connections.append(connection)
                print ("Someone connected from {}".format(client_address))
            # Else we have some data
            else:
                data = connection.recv(64)
                print('received {!r}'.format(data))
                if data:
                    print('sending data back to the client')
                    update = update_grid(data) # perhaps do this in another thread
                    connection.sendall(data)  # Perhaps do a broadcast here.
                else: #connection has closed
                    print ("closing the connection")
                    connections.remove(connection)
    # Handling stopping servers and closing connections.
    except KeyboardInterrupt:
        print ("Terminating and closing existing connections")
        for connection in connections:
            connection.close()



connection.close()
# Receive update  ->  update -> send back -> handle new connection
