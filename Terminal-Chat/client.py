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
            print(f"Received from server: {data.decode('utf-8')}")
        except ConnectionResetError:
            print("Connection with the server was reset.")
            break
        except Exception as e:
            print(f"An error occurred while receiving messages: {e}")
            break

# Define the server address (host and port)
ip_addr = input("Enter the server IP address: ")
server_host = ip_addr  # Replace with the actual IP address or hostname of the server
server_port = 12345

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    client_socket.connect((server_host, server_port))
    print(f"Connected to {server_host}:{server_port}")

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        # Get user input and send it to the server
        message = input("Enter a message to send to the server (type 'q' to quit): ")
        if message.lower() == 'q':
            break
        
        client_socket.sendall(message.encode('utf-8'))

except ConnectionRefusedError:
    print(f"Connection to {server_host}:{server_port} was refused. Check the server status and network settings.")
except KeyboardInterrupt:
    print("User interrupted the program.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the socket
    client_socket.close()
