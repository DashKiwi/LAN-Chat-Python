import socket
import sys
import threading
import os

HEADER_LENGTH = 10

# Prompt user for server details
while True:
    try:
        IP = input("Please enter an IP: ")
        PORT = int(input("Please enter a PORT: "))

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        client_socket.setblocking(False)
        print(f"Connected to server on {IP}:{PORT}")
        break
    except:
        print("Please try again. Server not found!")

# Get username
my_username = input("Username: ")
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)
print(f"Connected to server with username {my_username}")

# Do not delete. This helps ANSI Escape codes work on Windows
if os.name == "nt":
    os.system("")

def receive_messages():
    while True:
        try:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()

            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')

            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            print(f"\n{username} > {message}")
            print("\n> ", end='', flush=True)

        except Exception as e:
            continue

def send_messages():
    while True:
        message = input("\n> ")
        if message:
            message_encoded = message.encode('utf-8')
            message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message_encoded)

receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

send_messages()
