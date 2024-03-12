import socket
import threading
from cryptography.fernet import Fernet

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encryption_key = None

    def connect(self):
        self.client_socket.connect((self.host, self.port))

    def send_credentials(self, nickname, password):
        credentials = f"{nickname},{password}"
        self.client_socket.sendall(credentials.encode())

    def generate_key(self):
        return Fernet.generate_key()

    def encrypt_message(self, message, key):
        cipher_suite = Fernet(key)
        return cipher_suite.encrypt(message.encode())

    def decrypt_message(self, encrypted_message, key):
        cipher_suite = Fernet(key)
        return cipher_suite.decrypt(encrypted_message).decode()

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                decrypted_data = self.decrypt_message(data, self.encryption_key)
                print(decrypted_data)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_messages(self):
        while True:
            try:
                message = input()

                if message.startswith("/register") or message.startswith("/join_room") or message.startswith("/change_password"):
                    self.client_socket.sendall(self.encrypt_message(message, self.encryption_key))
                    response = self.client_socket.recv(1024).decode()
                    print(response)
                    continue

                encrypted_message = self.encrypt_message(message, self.encryption_key)
                self.client_socket.sendall(encrypted_message)
            except Exception as e:
                print(f"Error sending message: {e}")
                break

    def start_threads(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        send_thread = threading.Thread(target=self.send_messages)

        receive_thread.start()
        send_thread.start()

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 12345

    client = ChatClient(host, port)
    client.connect()

    nickname = input("Enter your nickname: ")
    password = input("Enter your password: ")

    client.send_credentials(nickname, password)

    encryption_key = client.client_socket.recv(1024)
    client.encryption_key = encryption_key

    client.start_threads()
