import socket
import select
import time

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
            current_time = time.strftime("%H:%M")
            
            # Prepare the message with time, username, and join message
            time_str = current_time.encode('utf-8')
            time_header = f"{len(time_str):<{HEADER_LENGTH}}".encode('utf-8')
            username_str = user["data"]
            username_header = f"{len(username_str):<{HEADER_LENGTH}}".encode('utf-8')
            message_encoded = join_message.encode('utf-8')
            message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
            
            # Send the join message to all clients (except the new one)
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(time_header + time_str + username_header + username_str + message_header + message_encoded)

        else:
            message = receive_message(notified_socket)
            if message is False:
                # Handle client disconnection
                user = clients[notified_socket]
                disconnect_message = "[Client has disconnected]"
                current_time = time.strftime("%H:%M")
                
                # Prepare the message with time, username, and disconnect message
                time_str = current_time.encode('utf-8')
                time_header = f"{len(time_str):<{HEADER_LENGTH}}".encode('utf-8')
                username_str = user["data"]
                username_header = f"{len(username_str):<{HEADER_LENGTH}}".encode('utf-8')
                message_encoded = disconnect_message.encode('utf-8')
                message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
                
                # Send the message to all clients (except the disconnected one)
                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(time_header + time_str + username_header + username_str + message_header + message_encoded)
                
                print("Closed connection from: {}".format(user["data"].decode("utf-8")))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
            for client_socket in clients:
                if client_socket != notified_socket:
                    time_str = str(time.strftime("%H:%M")).encode('utf-8')
                    time_header = f"{len(time_str):<{HEADER_LENGTH}}".encode('utf-8')
                    message_to_send = time_header + time_str + user["header"] + user["data"] + message["header"] + message["data"]
                    client_socket.send(message_to_send)

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
