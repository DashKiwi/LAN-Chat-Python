import socket
import select
import time
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False

HEADER_LENGTH = 10
FILE_HEADER_LENGTH = 20  # Increased for file data

while True:
    try:
        PORT = int(input("Please enter a PORT: "))
        if PORT <= 65535 and PORT >= 0:
            break
        else:
            raise
    except:
        print("Invalid PORT. Please choose a port between 0 and 65535")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(("", PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}

hostname = socket.gethostname()
IP = get_local_ip()
print(f"{hostname} is listening for connections on {IP}:{PORT}...")

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print("Accepted new connection from {}:{}, username: {}".format(*client_address, user["data"].decode("utf-8")))

            # Notify all other clients that a new client has joined
            join_message = "[Client has joined]"

            # Prepare the message with username, and join message
            username_str = user["data"]
            username_header = f"{len(username_str):<{HEADER_LENGTH}}".encode('utf-8')
            message_encoded = join_message.encode('utf-8')
            message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')

            # Send the join message to all clients (except the new one)
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(username_header + username_str + message_header + message_encoded)

        else:
            message = receive_message(notified_socket)
            if message is False:
                # Handle client disconnection
                user = clients[notified_socket]
                disconnect_message = "[Client has disconnected]"

                # Prepare the message with time, username, and disconnect message
                username_str = user["data"]
                username_header = f"{len(username_str):<{HEADER_LENGTH}}".encode('utf-8')
                message_encoded = disconnect_message.encode('utf-8')
                message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')

                # Send the message to all clients (except the disconnected one)
                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(username_header + username_str + message_header + message_encoded)

                print("Closed connection from: {}".format(user["data"].decode("utf-8")))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            # Check if it's a file transfer
            try:
                message_str = message['data'].decode('utf-8')
                print(f"Received message from {clients[notified_socket]['data'].decode('utf-8')}: {message_str}")
                for client_socket in clients:
                    if client_socket != notified_socket:
                        message_to_send = clients[notified_socket]["header"] + clients[notified_socket]["data"] + message["header"] + message["data"]
                        client_socket.send(message_to_send)
            except UnicodeDecodeError:
                # File transfer
                filename_header = notified_socket.recv(FILE_HEADER_LENGTH)
                filename_length = int(filename_header.decode('utf-8').strip())
                filename = notified_socket.recv(filename_length).decode('utf-8')

                print(f"Received file '{filename}' from {clients[notified_socket]['data'].decode('utf-8')}")

                # Forward file to all other clients.
                for client_socket in clients:
                    if client_socket != notified_socket:
                        message_to_send = clients[notified_socket]["header"] + clients[notified_socket]["data"] + message["header"] + message["data"]
                        client_socket.send(message_to_send)
                        client_socket.send(filename_header + filename.encode('utf-8'))

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]