import socket
import threading

# Define the server address (host and port)
host = '127.0.0.1'  # Listen on all available interfaces
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
client_nicknames = {}
online_clients = set()

def handle_client(client_socket, client_address):
    try:
        # Get the nickname from the client
        nickname_data = client_socket.recv(1024)
        nickname = nickname_data.decode().strip()
        client_nicknames[client_socket] = nickname
        online_clients.add(client_socket)

        # Send a welcome message and request nickname from the client
        client_socket.sendall(f"Welcome, {nickname}! Type the command '/list_clients' to see who's online.".encode())

        # Broadcast a notification when a client connects
        for other_client_socket in client_sockets:
            if other_client_socket != client_socket:
                other_client_socket.sendall(f"{nickname} has joined.".encode())

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            decoded_data = data.decode()
            if decoded_data.startswith("/list_clients"):
                # Send a list of connected clients to the requesting client
                client_socket.sendall(str(client_nicknames.values()).encode())
            elif decoded_data.startswith("/server_broadcast"):
                # Broadcast a server message to all clients
                message = "Server: " + "from" + decoded_data[len("/server_broadcast"):].strip()
                for other_client_socket in client_sockets:
                    if other_client_socket != client_socket:
                        other_client_socket.sendall(message.encode())
            elif decoded_data.startswith("/private"):
                # Extract the target username and message
                _, target_username, message = decoded_data.split(" ", 2)
                target_client = next((sock for sock, nick in client_nicknames.items() if nick == target_username), None)
                if target_client:
                    target_client.sendall(f"Private message from {nickname}: {message}".encode())
                else:
                    client_socket.sendall("User not found.".encode())
            else:
                # Broadcast the message to all other clients with sender's address
                message = f"{nickname}: {decoded_data}"
                for other_client_socket in client_sockets:
                    if other_client_socket != client_socket:
                        other_client_socket.sendall(message.encode())
    except Exception as e:
        print(f"Client {client_address} disconnected: {e}")
    finally:
        try:
            online_clients.remove(client_socket)
            client_sockets.remove(client_socket)
        except Exception as e:
            print(f"Error during socket removal: {e}")
        finally:
            client_socket.close()

while True:
    try:
        # Accept a connection from a client
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Add the new client socket to the list
        client_sockets.append(client_socket)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
    except Exception as e:
        print(f"An error occurred while accepting a connection: {e}")
