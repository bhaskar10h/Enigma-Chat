import socket
import threading

def receive_messages(client_socket):
    while True:
        # Receive and print messages from the server
        data = client_socket.recv(1024)
        print(f"Received from server: {data.decode('utf-8')}")

# Define the server address (host and port)
host = '127.0.0.1'
port = 12345

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((host, port))
print(f"Connected to {host}:{port}")

# Start a thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.start()

try:
    while True:
        # Get user input and send it to the server
        message = input("Enter a message to send to the server (type 'exit' to quit): ")
        
        if message.lower() == 'exit':
            break
        
        client_socket.sendall(message.encode('utf-8'))

except KeyboardInterrupt:
    print("Client interrupted.")

finally:
    # Close the socket
    client_socket.close()
