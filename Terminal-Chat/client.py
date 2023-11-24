import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            # Receive and print messages from the server
            data = client_socket.recv(1024)
            if not data:
                print("Connection with the server was closed.")
                break
            print(f"Server: {data.decode('utf-8')}")
        except ConnectionResetError:
            print("Connection with the server was reset.")
            break
        except Exception as e:
            print(f"An error occurred while receiving messages: {e}")
            break

# Define the server address (host and port)
server_host = '127.0.0.1'
server_port = 12345

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    client_socket.connect((server_host, server_port))
    print(f"Connected to the server at {server_host}:{server_port}")

    # Set your nickname for the chat
    nickname = input("Set your nickname: ")
    client_socket.sendall(nickname.encode('utf-8'))

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        # Get user input and send it to the server
        message = input("Your message (type '/private <username> <message>' for private messages, 'q' to quit): ")
        if message.lower() == 'q':
            break
        
        client_socket.sendall(message.encode('utf-8'))

except ConnectionRefusedError:
    print(f"Connection to the server at {server_host}:{server_port} was refused. Check the server status and network settings.")
except KeyboardInterrupt:
    print("You interrupted the program.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the socket
    client_socket.close()
