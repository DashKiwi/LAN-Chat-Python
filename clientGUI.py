import socket
import sys
import threading
import os
import select
import tkinter as tk
from tkinter import scrolledtext

HEADER_LENGTH = 10

# Function to create a socket connection
def connect_to_server():
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
    
    return client_socket, my_username

# Receive messages and display them in the GUI's text area
def receive_messages(client_socket, text_area):
    while True:
        try:
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

                text_area.config(state=tk.NORMAL)  # Allow editing
                text_area.insert(tk.END, f"\n{time} {username} > {message}")
                text_area.yview(tk.END)  # Auto-scroll to the bottom
                text_area.config(state=tk.DISABLED)  # Disable editing

        except BlockingIOError:
            continue
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Send messages from the GUI text box
def send_message(client_socket, entry_widget, text_area):
    message = entry_widget.get()
    if message:
        try:
            # Send message to server
            message_encoded = message.encode('utf-8')
            message_header = f"{len(message_encoded):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message_encoded)

            # Display the sent message in the message box
            text_area.config(state=tk.NORMAL)
            text_area.insert(tk.END, f"\nYou > {message}")
            text_area.yview(tk.END)
            text_area.config(state=tk.DISABLED)

            # Clear the text entry after sending
            entry_widget.delete(0, tk.END)  
        except Exception as e:
            print(f"Error sending message: {e}")

# Create the Tkinter window and its components
def create_gui(client_socket):
    window = tk.Tk()
    window.title("Chat Client")
    
    # Create message display box
    text_area = scrolledtext.ScrolledText(window, width=50, height=15, wrap=tk.WORD, state=tk.DISABLED)
    text_area.grid(row=0, column=0, padx=10, pady=10)
    
    # Create message entry box
    entry_widget = tk.Entry(window, width=40)
    entry_widget.grid(row=1, column=0, padx=10, pady=10)
    
    # Create send button
    send_button = tk.Button(window, text="Send", width=10, command=lambda: send_message(client_socket, entry_widget, text_area))
    send_button.grid(row=1, column=1, padx=10, pady=10)
    
    # Bind Enter key to send message
    entry_widget.bind('<Return>', lambda event: send_message(client_socket, entry_widget, text_area))

    # Start receiving messages in a separate thread
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_area), daemon=True)
    receive_thread.start()
    
    # Start the Tkinter event loop
    window.mainloop()

if __name__ == "__main__":
    client_socket, my_username = connect_to_server()
    create_gui(client_socket)
