import socket
import errno
import sys
import threading
import os
import time
import keyboard

HEADER_LENGTH = 10
while True:
    try:
        IP = input("Please enter a IP: ")
        PORT = int(input("Please enter a PORT: "))

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_socket.connect((IP, PORT))
        client_socket.setblocking(False)
        print(f"Connected to server on {IP}:{PORT}")
        break
    except:
        print("Please try again. Server not found!")

send_message = ""

my_username = input("Username: ")
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)
print(f"Connected to server with username {my_username}")

# Do not delete. For some reason makes the ANSI Escape codes work
if os.name == "nt":
    os.system("")

def send_msg_to_server():
    global send_message
    while True:
        # Check if spacebar is pressed
        if keyboard.is_pressed("space"):
            send_message += " "
            print(f"{send_message}", end='\r', flush=True)  # Overwrite the current line
            time.sleep(0.1)  # Add a small delay to prevent multiple key reads

        # Check if another key is pressed (excluding enter and shift)
        elif not keyboard.is_pressed("enter") and not keyboard.is_pressed("shift"):
            key_event = keyboard.read_event(suppress=True)  # Read the key event
            if key_event.event_type == keyboard.KEY_DOWN:  # Check if the key was pressed down
                key = key_event.name
                if len(key) == 1:  # Avoid non-printable keys (shift, enter, etc.)
                    send_message += key
                    print(f"{send_message}", end='\r', flush=True)  # Overwrite the current line
            time.sleep(0.1)  # Add a small delay to prevent multiple key reads

        # Handle Enter key press (send message to the server)
        elif keyboard.read_event(suppress=True).name == "enter" and send_message:
            # Send the message to the server
            message_encoded = send_message.encode('utf-8')
            message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message_encoded)
            print(f"\033[F\033[K{my_username} > {send_message}")  # Display the message on the screen
            send_message = ""

threading.Thread(target=send_msg_to_server).start()

while True:
    try:
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            print(f"\r{username} > {message}\n{send_message}")

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue

    except Exception as e:
        print('Reading error: {}'.format(str(e)))
        sys.exit()