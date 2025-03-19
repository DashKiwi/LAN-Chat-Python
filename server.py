import socket
import select
import time
import os

# Function to get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# Function to receive messages from a client
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        data = client_socket.recv(message_length)
        return {"header": message_header, "data": data}
    except:
        return False

HEADER_LENGTH = 10

# Ask for port number
while True:
    try:
        PORT = int(input("Please enter a PORT: "))
        if PORT <= 65535 and PORT >= 0:
            break
        else:
            raise
    except:
        print("Invalid PORT. Please choose a port between 0 and 65535")

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(("", PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}

hostname = socket.gethostname()
IP = get_local_ip()
print(f"{hostname} is listening for connections on {IP}:{PORT}...")

# Function to send media files to all clients except the sender
def send_media_to_all_clients(sender_socket, media_data, media_header, media_type):
    for client_socket in clients:
        if client_socket != sender_socket:
            prefix = b'IMG:' if media_type == "image" else b'GIF:'
            prefix = f"{prefix}".encode('utf-8')
            client_socket.send(media_header + prefix + media_data)

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            # Handle new client connection
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]}, username: {user['data'].decode('utf-8')}")

            # Notify all other clients about the new user
            join_message = "[Client has joined]"
            username_str = user["data"]
            username_header = f"{len(username_str):<{HEADER_LENGTH}}".encode('utf-8')
            message_encoded = join_message.encode('utf-8')
            message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(username_header + username_str + message_header + message_encoded)

        else:
            # Receive a message (text or media)
            message = receive_message(notified_socket)
            if message is False:
                # Handle client disconnection
                user = clients[notified_socket]
                disconnect_message = "[Client has disconnected]"
                username_str = user["data"]
                username_header = f"{len(username_str):<{HEADER_LENGTH}}".encode('utf-8')
                message_encoded = disconnect_message.encode('utf-8')
                message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')

                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(username_header + username_str + message_header + message_encoded)

                print(f"Closed connection from: {user['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            # Check if the message is a media file (image/GIF)
            user = clients[notified_socket]
            message_data = message["data"]
            if message_data.startswith(b'IMG:') or message_data.startswith(b'GIF:'):
                print(f"Received media file from {user['data'].decode('utf-8')}")
                media_type = "image" if message_data.startswith(b'IMG:') else "gif"
                media_data = message_data[4:]  # Remove 'IMG:' or 'GIF:'
                media_header = f"{len(media_data):<{HEADER_LENGTH}}".encode('utf-8')
                
                # Send the media data to all other clients
                send_media_to_all_clients(notified_socket, media_data, media_header, media_type)

            else:
                # If it's a regular text message
                print(f"Received message from {user['data'].decode('utf-8')}: {message_data.decode('utf-8')}")
                for client_socket in clients:
                    if client_socket != notified_socket:
                        message_to_send = user["header"] + user["data"] + message["header"] + message["data"]
                        client_socket.send(message_to_send)

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
