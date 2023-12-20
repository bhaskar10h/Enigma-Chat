import socket
import threading
from cryptography.fernet import Fernet

# Server address (host and port)
host = '127.0.0.1'
port = 12345

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((host, port))

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            # Decrypt the received message
            decrypted_data = decrypt_message(data, encryption_key)
            print(decrypted_data)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Function to send messages to the server
def send_messages():
    while True:
        try:
            message = input()

            if message.startswith("/register"):
                # Handle user registration
                client_socket.sendall(encrypt_message(message, encryption_key))
                response = client_socket.recv(1024).decode()
                print(response)
                continue
            elif message.startswith("/join_room"):
                # Handle joining a room
                client_socket.sendall(encrypt_message(message, encryption_key))
                response = client_socket.recv(1024).decode()
                print(response)
                continue
            elif message.startswith("/change_password"):
                # Handle changing password
                client_socket.sendall(encrypt_message(message, encryption_key))
                response = client_socket.recv(1024).decode()
                print(response)
                continue

            # Encrypt the message before sending
            encrypted_message = encrypt_message(message, encryption_key)
            client_socket.sendall(encrypted_message)
        except Exception as e:
            print(f"Error sending message: {e}")
            break

# Function to generate a key and create a cipher suite
def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(message.encode())

def decrypt_message(encrypted_message, key):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_message).decode()

# Get user credentials
nickname = input("Enter your nickname: ")
password = input("Enter your password: ")

# Send user credentials to the server
credentials = f"{nickname},{password}"
client_socket.sendall(credentials.encode())

# Receive the encryption key from the server
encryption_key = client_socket.recv(1024)

# Start threads for sending and receiving messages
receive_thread = threading.Thread(target=receive_messages)
send_thread = threading.Thread(target=send_messages)

receive_thread.start()
send_thread.start()
