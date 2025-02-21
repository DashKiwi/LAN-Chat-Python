import socket
import sys
import threading
import os
import select  # Import select module

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
    except Exception as e:
        print(f"Please try again. Server not found! Error: {e}")

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
            # Use select to check if the socket is ready for reading
            ready_to_read, _, _ = select.select([client_socket], [], [], 0.1)
            if ready_to_read:
                # Try receiving data
                time_header = client_socket.recv(HEADER_LENGTH)
                if not len(time_header):
                    print("Connection closed by the server")
                    sys.exit()

                time_length = int(time_header.decode('utf-8').strip())
                time = client_socket.recv(time_length).decode('utf-8')

                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("Connection closed by the server")
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                print(f"\n{time} {username} > {message}")
                print("> ", end='', flush=True)

        except BlockingIOError:
            continue
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def send_messages():
    while True:
        message = input("> ")
        if message:
            try:
                message_encoded = message.encode('utf-8')
                message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message_encoded)
            except Exception as e:
                print(f"Error sending message: {e}")
                break

receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

send_messages()