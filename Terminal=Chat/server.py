import socket
import threading

# Define the server address (host and port)
host = '127.0.0.1'
port = 12345

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind((host, port))

# Listen for incoming connections (max 5 connections in the queue)
server_socket.listen(5)
print(f"Server listening on {host}:{port}")

# List to store client sockets
client_sockets = []

def handle_client(client_socket):
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        
        if not data:
            break  # Connection closed by the client
        
        # Send the received data to all other clients
        for other_client_socket in client_sockets:
            if other_client_socket != client_socket:
                other_client_socket.sendall(data)

    # Remove the closed client's socket from the list
    client_sockets.remove(client_socket)
    client_socket.close()

while True:
    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    # Add the new client socket to the list
    client_sockets.append(client_socket)

    # Start a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
