import socket
import threading
import logging
from cryptography.fernet import Fernet

logging.basicConfig(filename='server_log.txt', level=logging.INFO)

host = '127.0.0.1'
port = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)
print(f"Server listening on {host}:{port}")

client_sockets = []
client_nicknames = {}
online_clients = set()
user_credentials = {'user1': 'password1', 'user2': 'password2'}
private_rooms = {}
encryption_keys = {}

def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(message.encode())

def decrypt_message(encrypted_message, key):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_message).decode()

def register_user(username, password):
    if username not in user_credentials:
        user_credentials[username] = password
        return True
    else:
        return False

def change_password(username, new_password):
    if username in user_credentials:
        user_credentials[username] = new_password
        return True
    else:
        return False

def handle_client(client_socket, client_address):
    try:
        nickname_data = client_socket.recv(1024)
        nickname, password = nickname_data.decode().split(',')

        if nickname in user_credentials and user_credentials[nickname] == password:
            client_nicknames[client_socket] = nickname
            online_clients.add(client_socket)
            encryption_key = generate_key()
            encryption_keys[client_socket] = encryption_key
            client_socket.sendall(f"Welcome, {nickname}! Type the command '/list_clients' to see who's online.".encode())
            broadcast_user_status(f"{nickname} has joined.")
            client_socket.sendall(encryption_key)
        else:
            client_socket.sendall("Invalid credentials. Disconnecting.".encode())
            return

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            decoded_data = decrypt_message(data, encryption_keys[client_socket])

            if decoded_data.startswith("/list_clients"):
                client_socket.sendall(str(list(client_nicknames.values())).encode())
            elif decoded_data.startswith("/server_broadcast"):
                message = "Server: " + "from" + decoded_data[len("/server_broadcast"):].strip()
                for other_client_socket in client_sockets:
                    if other_client_socket != client_socket:
                        other_client_socket.sendall(message.encode())
            elif decoded_data.startswith("/private"):
                _, target_username, message = decoded_data.split(" ", 2)
                target_client = next((sock for sock, nick in client_nicknames.items() if nick == target_username), None)
                if target_client:
                    target_client.sendall(f"Private message from {nickname}: {message}".encode())
                else:
                    client_socket.sendall("User not found.".encode())
            elif decoded_data.startswith("/custom_command"):
                client_socket.sendall("This is a custom command response.".encode())
            elif decoded_data.startswith("/register"):
                _, register_username, register_password = decoded_data.split(" ", 2)
                if register_user(register_username, register_password):
                    client_socket.sendall("Registration successful. You can now log in.".encode())
                else:
                    client_socket.sendall("Username already exists. Choose a different one.".encode())
            elif decoded_data.startswith("/create_room"):
                room_name = decoded_data.split(" ", 1)[1]
                private_rooms[room_name] = set([client_socket])
                client_socket.sendall(f"Room '{room_name}' created. You are the owner.".encode())
            elif decoded_data.startswith("/join_room"):
                room_name = decoded_data.split(" ", 1)[1]
                if room_name in private_rooms:
                    private_rooms[room_name].add(client_socket)
                    client_socket.sendall(f"Joined room '{room_name}'.".encode())
                else:
                    client_socket.sendall(f"Room '{room_name}' does not exist.".encode())
            elif decoded_data.startswith("/leave_chat"):
                client_socket.sendall("Leaving the chat. Goodbye!".encode())
                break
            else:
                message = f"{nickname}: {decoded_data}"
                for other_client_socket in client_sockets:
                    if other_client_socket != client_socket:
                        other_client_socket.sendall(encrypt_message(message, encryption_keys[other_client_socket]))
    except Exception as e:
        logging.error(f"Client {client_address} disconnected: {e}")
    finally:
        try:
            online_clients.remove(client_socket)
            client_sockets.remove(client_socket)
            broadcast_user_status(f"{nickname} has left.")
            del encryption_keys[client_socket]
        except Exception as e:
            logging.error(f"Error during socket removal: {e}")
        finally:
            client_socket.close()

def broadcast_user_status(status_message):
    for other_client_socket in client_sockets:
        other_client_socket.sendall(encrypt_message(status_message, encryption_keys[other_client_socket]))

while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")

        client_sockets.append(client_socket)

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
    except Exception as e:
        print(f"An error occurred while accepting a connection: {e}")
