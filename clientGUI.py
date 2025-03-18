import socket
import sys
import threading
import select
import tkinter as tk
import json
import os
import time
from tkinter import scrolledtext, Toplevel, simpledialog, filedialog

current_theme_window = None
ip_entry = None
port_entry = None
username_entry = None

HEADER_LENGTH = 10

def set_path():
    global application_path, THEME_FILE, SERVERS_FILE
    if getattr(sys, 'frozen', False):
        # Running as a packaged executable
        application_path = os.path.dirname(sys.executable)
    else:
        # Running as a Python script
        application_path = os.path.dirname(__file__)
    THEME_FILE = os.path.join(application_path, "themes.json")
    SERVERS_FILE = os.path.join(application_path, "servers.json")

def save_themes():
    global THEME_FILE
    with open(THEME_FILE, "w") as file:
        json.dump(THEMES, file, indent=4)

def apply_theme(window, text_area, entry_widget, send_button):
    theme = THEMES[current_theme]
    window.configure(bg=theme["bg"])
    text_area.config(bg=theme["bg"], fg=theme["fg"])
    entry_widget.config(bg=theme["entry_bg"], fg=theme["entry_fg"])
    send_button.config(bg=theme["entry_bg"], fg=theme["entry_fg"])

def open_theme_selector(window, text_area, entry_widget, send_button):
    global current_theme_window
    theme_window = Toplevel(window)
    theme_window.title("Select Theme")
    theme_window.geometry("200x250")
    
    # Store the reference of the theme_window in the global variable
    # Close the old theme selector window if it's open
    if current_theme_window:
        current_theme_window.destroy()  # This closes the old theme selector window
    current_theme_window = theme_window
    
    # Create a Canvas widget for scrolling
    canvas = tk.Canvas(theme_window)
    canvas.grid(row=0, column=0, sticky="nsew")  # Expand to all directions in grid
    
    # Create a Scrollbar linked to the canvas
    scrollbar = tk.Scrollbar(theme_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")  # Place scrollbar to the right
    
    # Configure the canvas to work with the scrollbar
    canvas.config(yscrollcommand=scrollbar.set)
    
    # Create a frame inside the canvas to contain the theme buttons
    button_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=button_frame, anchor="nw")
    
    # Add the theme buttons to the button_frame
    for theme in THEMES.keys():
        if theme != "Selected_theme":
            tk.Button(button_frame, text=theme, command=lambda t=theme: set_theme(t, window, text_area, entry_widget, send_button)).pack(pady=5)
    
    # Add the custom theme, export, and import buttons
    tk.Button(button_frame, text="Create Custom Theme", command=lambda: create_custom_theme(window, text_area, entry_widget, send_button)).pack(pady=5)
    tk.Button(button_frame, text="Export Themes", command=export_themes).pack(pady=5)
    tk.Button(button_frame, text="Import Themes", command=lambda: import_themes(window, text_area, entry_widget, send_button)).pack(pady=5)
    
    # Update the scroll region of the canvas after adding buttons
    button_frame.update_idletasks()  # Ensure frame size is updated before setting scroll region
    canvas.config(scrollregion=canvas.bbox("all"))  # Set the scroll region to the bounds of all items in the canvas
    
    # Configure grid row and column weights to allow resizing
    theme_window.grid_rowconfigure(0, weight=1)  # Allow row 0 (Canvas) to expand
    theme_window.grid_columnconfigure(0, weight=1)  # Allow column 0 (Canvas) to expand

def set_theme(theme, window, text_area, entry_widget, send_button):
    global current_theme
    current_theme = theme
    THEMES["Selected_theme"] = theme
    with open(THEME_FILE, "w") as file:
        json.dump(THEMES, file, indent=4)
    apply_theme(window, text_area, entry_widget, send_button)
    save_themes()

def create_custom_theme(window, text_area, entry_widget, send_button):
    theme_name = simpledialog.askstring("Custom Theme", "Enter theme name:")
    if not theme_name:
        return
    
    bg_color = simpledialog.askstring("Custom Theme", "Enter background color (hex or name):")
    if not bg_color:
        return
    fg_color = simpledialog.askstring("Custom Theme", "Enter text color (hex or name):")
    if not fg_color:
        return
    entry_bg_color = simpledialog.askstring("Custom Theme", "Enter entry background color (hex or name):")
    if not entry_bg_color:
        return
    entry_fg_color = simpledialog.askstring("Custom Theme", "Enter entry text color (hex or name):")
    if not entry_fg_color:
        return
    
    THEMES[theme_name] = {
        "bg": bg_color,
        "fg": fg_color,
        "entry_bg": entry_bg_color,
        "entry_fg": entry_fg_color
    }
    
    save_themes()
    set_theme(theme_name, window, text_area, entry_widget, send_button)

    # Update theme selector to include the new theme
    open_theme_selector(window, text_area, entry_widget, send_button)

def export_themes():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "w") as file:
            json.dump(THEMES, file, indent=4)

def import_themes(window, text_area, entry_widget, send_button):
    global THEMES, current_theme_window
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "r") as file:
            imported_themes = json.load(file)
            imported_themes.pop("Selected_theme", None)     
            THEMES.update(imported_themes)
            save_themes()
            
            # Reapply the current theme after importing new themes
            apply_theme(window, text_area, entry_widget, send_button)

            # Close the old theme selector window if it exists
            if current_theme_window:
                current_theme_window.destroy()

            # Open the theme selector again with the updated list
            open_theme_selector(window, text_area, entry_widget, send_button)

def connect_to_server(ip, port, username):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(2)
        client_socket.connect((ip, port))
        client_socket.setblocking(False)
        
        username_encoded = username.encode('utf-8')
        username_header = f"{len(username_encoded):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(username_header + username_encoded)

        return client_socket
    except:
        return(f"Please try again. Server Unresponsive!")

# Receive messages and display them in the GUI's text area
def receive_messages(client_socket, text_area):
    while True:
        try:
            ready_to_read, _, _ = select.select([client_socket], [], [], 0.1)
            if ready_to_read:
                # Try receiving data
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("Connection closed by the server")
                    sys.exit()
                
                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')
                
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')
                
                local_time = time.strftime("%H:%M")

                text_area.config(state=tk.NORMAL)  # Allow editing
                text_area.insert(tk.END, f"\n{local_time} {username} > {message}")
                text_area.yview(tk.END)  # Auto-scroll to the bottom
                text_area.config(state=tk.DISABLED)  # Disable editing
        except BlockingIOError:
            continue
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def send_media(client_socket, file_path, media_type):
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        # Add prefix to indicate file type
        prefix = b'IMG:' if media_type == "image" else b'GIF:'
        message = prefix + file_data
        
        # Create message header
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        
        # Send header + data
        client_socket.send(message_header + message)
        print(f"Sent {media_type} file: {os.path.basename(file_path)}")
    
    except Exception as e:
        print(f"Error sending file: {e}")

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

def try_connect(ip_entry, port_entry, username_entry, error_label, root):
        error_label.config(text="Checking Fields", fg="red")
        ip = ip_entry.get().strip()
        port = port_entry.get().strip()
        username = username_entry.get().strip()

        if not ip or not port or not username:
            error_label.config(text="All fields are required!", fg="red")
            return

        try:
            port = int(port)
            if port <= 0 or port > 65535:
                raise ValueError("Invalid port number.")

            connection_result = connect_to_server(ip, port, username)
            if isinstance(connection_result, str):  # If it's an error message
                error_label.config(text=f"Error: {connection_result}", fg="red")
            else:
                root.destroy()  # Close the connection window
                create_gui(connection_result)  # Start chat GUI

        except ValueError as e:
            error_label.config(text=f"Error: {e}", fg="red")

def show_connection_window():
    global ip_entry, port_entry, username_entry  # Mark as global

    root = tk.Tk()
    root.title("Connect to Server")

    tk.Label(root, text="IP Address:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ip_entry = tk.Entry(root, width=30)  # Assign to global variable
    ip_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Port:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    port_entry = tk.Entry(root, width=30)  # Assign to global variable
    port_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(root, text="Username:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    username_entry = tk.Entry(root, width=30)  # Assign to global variable
    username_entry.grid(row=2, column=1, padx=5, pady=5)

    error_label = tk.Label(root, text="", fg="red")
    error_label.grid(row=5, column=0, columnspan=2)

    connect_button = tk.Button(root, text="Connect", command=lambda: try_connect(ip_entry, port_entry, username_entry, error_label, root))
    connect_button.grid(row=3, column=0, columnspan=2, pady=10)

    prev_connections_button = tk.Button(root, text="Previous Connections", command=lambda: open_previous_connections(root))
    prev_connections_button.grid(row=4, column=0, columnspan=2, pady=5)

    root.mainloop()

def open_previous_connections(parent):
    prev_window = Toplevel(parent)
    prev_window.title("Previous Connections")
    prev_window.geometry("300x300")

    servers = load_saved_servers()
    
    server_listbox = tk.Listbox(prev_window, width=40, height=10)
    server_listbox.pack(pady=10)

    for server in servers:
        server_listbox.insert(tk.END, f"{server['name']} ({server['ip']}:{server['port']})")

    join_button = tk.Button(prev_window, text="Join Server", command=lambda: join_selected(server_listbox, servers, prev_window))
    join_button.pack(pady=5)

    add_button = tk.Button(prev_window, text="Add Server", command=lambda: add_edit_server_window(servers, prev_window))
    add_button.pack(pady=5)

    edit_button = tk.Button(prev_window, text="Edit Server", command=lambda: edit_selected(server_listbox, servers, prev_window))
    edit_button.pack(pady=5)

def join_selected(server_listbox, servers, prev_window):
    global ip_entry, port_entry, username_entry

    selection = server_listbox.curselection()
    if selection:
        selected = servers[selection[0]]
        ip_entry.delete(0, tk.END)
        ip_entry.insert(0, selected["ip"])
        port_entry.delete(0, tk.END)
        port_entry.insert(0, selected["port"])
        username_entry.delete(0, tk.END)
        username_entry.insert(0, selected["name"])
        prev_window.destroy()

def edit_selected(server_listbox, servers, parent):
    selection = server_listbox.curselection()
    if selection:
        add_edit_server_window(servers, parent, selection[0])

def add_edit_server_window(servers, parent, index=None):
    add_edit_window = Toplevel(parent)
    add_edit_window.title("Add/Edit Server")
    add_edit_window.geometry("250x200")

    tk.Label(add_edit_window, text="IP Address:").pack()
    ip_entry = tk.Entry(add_edit_window)
    ip_entry.pack()

    tk.Label(add_edit_window, text="Port:").pack()
    port_entry = tk.Entry(add_edit_window)
    port_entry.pack()

    tk.Label(add_edit_window, text="Username:").pack()
    name_entry = tk.Entry(add_edit_window)
    name_entry.pack()

    if index is not None:
        ip_entry.insert(0, servers[index]["ip"])
        port_entry.insert(0, servers[index]["port"])
        name_entry.insert(0, servers[index]["name"])

    save_button = tk.Button(add_edit_window, text="Save", command=lambda: save_server(servers, index, name_entry, ip_entry, port_entry, add_edit_window, parent))
    save_button.pack(pady=5)

    if index is not None:
        delete_button = tk.Button(add_edit_window, text="Delete", command=lambda: delete_server(servers, index, add_edit_window, parent))
        delete_button.pack(pady=5)

def save_server(servers, index, name_entry, ip_entry, port_entry, window, parent):
    new_server = {"name": name_entry.get(), "ip": ip_entry.get(), "port": port_entry.get()}
    if index is None:
        servers.append(new_server)
    else:
        servers[index] = new_server
    save_servers(servers)
    window.destroy()
    if parent.winfo_exists():  # Check if parent still exists before destroying
        parent.destroy()
    open_previous_connections(parent.master)

def delete_server(servers, index, window, parent):
    del servers[index]
    save_servers(servers)
    window.destroy()
    if parent.winfo_exists():
        parent.destroy()
    open_previous_connections(parent.master, None, None, None)

def load_saved_servers():
    if os.path.exists(SERVERS_FILE):
        with open(SERVERS_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def save_servers(servers):
    with open(SERVERS_FILE, "w") as file:
        json.dump(servers, file, indent=4)

# Create the Tkinter window and its components
def create_gui(client_socket):
    window = tk.Tk()
    window.title("Chat Client")
    
    # Create message display box
    text_area = scrolledtext.ScrolledText(window, width=50, height=15, wrap=tk.WORD, state=tk.DISABLED)
    text_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    
    # Create message entry box
    entry_widget = tk.Entry(window, width=40)
    entry_widget.grid(row=1, column=0, padx=10, pady=10)
    
    # Create send button
    send_button = tk.Button(window, text="Send", width=10, command=lambda: send_message(client_socket, entry_widget, text_area))
    send_button.grid(row=1, column=1, padx=10, pady=10)
    
    # Bind Enter key to send message
    entry_widget.bind('<Return>', lambda event: send_message(client_socket, entry_widget, text_area))
    
    # Start receiving messages in a separate thread
    theme_button = tk.Button(window, text="Change Theme", command=lambda: open_theme_selector(window, text_area, entry_widget, send_button))
    theme_button.grid(row=2, column=0, columnspan=2, pady=5)
    
    apply_theme(window, text_area, entry_widget, send_button)
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_area), daemon=True)
    receive_thread.start()
    
    # Start the Tkinter event loop
    window.mainloop()

set_path()
THEMES = {
        "Light": {"bg": "white", "fg": "black", "entry_bg": "white", "entry_fg": "black"},
        "Dark": {"bg": "#2E2E2E", "fg": "white", "entry_bg": "#3E3E3E", "entry_fg": "white"},
        "Selected_theme": "Dark"
    }

try:
    # Ensure themes.json file exists
    if not os.path.exists(THEME_FILE) or os.stat(THEME_FILE).st_size == 0:
        with open(THEME_FILE, "w") as file:
            json.dump(THEMES, file, indent=4)

    # Load existing themes
    with open(THEME_FILE, "r") as file:
        try:
            data = json.load(file)  # Try to read JSON
        except json.JSONDecodeError:
            data = THEMES  # If file is empty or corrupted, reset data
            with open(THEME_FILE, "w") as file:
                json.dump(data, file, indent=4)

    # Ensure required themes exist
    if "Light" not in data or "Dark" not in data:
        data.update(THEMES)

        # Save updated themes
        with open(THEME_FILE, "w") as file:
            json.dump(data, file, indent=4)

    THEMES = data  # Update global THEMES with loaded data
except:
    pass

current_theme = THEMES["Selected_theme"]

if __name__ == "__main__":
    #client_socket, my_username = connect_to_server()
    #create_gui(client_socket)
    # Load themes from file
    show_connection_window()
