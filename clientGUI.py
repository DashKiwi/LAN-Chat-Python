import socket
import sys
import threading
import select
import tkinter as tk
import json
import os
import time
from tkinter import scrolledtext, Toplevel, simpledialog, filedialog, colorchooser, scrolledtext
from PIL import Image, ImageTk, ImageSequence
import io

current_theme_window = None
ip_entry = None
port_entry = None
username_entry = None

HEADER_LENGTH = 10
FILE_HEADER_LENGTH = 20

emojis = {
        ":grinning:": "😀", ":grin:": "😃", ":joy:": "😂", ":rolling_on_the_floor_laughing:": "🤣", ":smile:": "😄",
    ":smiling_face_with_tear:": "🥲", ":sweat_smile:": "😅", ":laughing:": "😆",":innocent:": "😇", ":wink:": "😉", ":blush:": "😊", ":slightly_smiling:": "🙂", ":upside_down:": "🙃",
    ":relaxed:": "😌", ":heart_eyes:": "😍", ":kissing_heart:": "😘", ":kissing:": "😗", ":kissing_smiling_eyes:": "😙", ":kissing_closed_eyes:": "😚", ":yum:": "😋",
    ":stuck_out_tongue:": "😛", ":stuck_out_tongue_winking_eye:": "😜", ":zany_face:": "🤪", ":raised_eyebrow:": "🤨", ":thinking:": "🤔", ":nerd:": "🤓", ":sunglasses:": "😎",
    ":star_struck:": "🤩", ":partying_face:": "🥳", ":smirk:": "😏", ":unamused:": "😒", ":disappointed:": "😞", ":pensive:": "😔", ":worried:": "😟", ":confused:": "😕",
    ":slightly_frowning:": "🙁", ":pleading_face:": "🥺", ":cry:": "😢", ":sob:": "😭", ":astonished:": "😲", ":open_mouth:": "😮", ":scream:": "😱", ":flushed:": "😳",
    ":frowning:": " frown", ":anguished:": "😧", ":fearful:": "😨", ":cold_sweat:": "😰", ":persevere:": " persevering", ":confounded:": "😖", ":tired_face:": "😫", ":weary:": "😩",
    ":triumph:": "😤", ":angry:": "😠", ":rage:": "😡", ":no_mouth:": "😶", ":neutral_face:": "😐", ":expressionless:": "😑", ":grimacing:": " grimace", ":lying_face:": "🤥",
    ":shushing_face:": "🤫", ":hand_over_mouth:": "🤭", ":thinking_face:": "🤔", ":zipper_mouth:": "🤐", ":raised_eyebrow:": "🤨", ":monocle_face:": "🧐", ":sleeping:": "😴",
    ":dizzy_face:": "😵", ":exploding_head:": "🤯", ":cowboy:": "🤠", ":clown:": "🤡", ":nauseated_face:": "🤢", ":vomiting_face:": "🤮", ":sneezing_face:": "🤧", ":hot_face:": "🥵",
    ":cold_face:": "🥶", ":woozy_face:": "🥴", ":face_with_symbols_over_mouth:": "🤬", ":face_with_spiral_eyes:": "😵‍💫", ":skull:": "💀", ":skull_and_crossbones:": "☠️",
    ":ghost:": "👻", ":alien:": "👽", ":robot:": "🤖", ":poop:": "💩", ":smiling_cat_with_heart_eyes:": "😻", ":see_no_evil:": "🙈", ":hear_no_evil:": "🙉",
    ":speak_no_evil:": "🙊", ":wave:": "👋", ":raised_back_of_hand:": "🤚", ":raised_hand:": "✋", ":vulcan_salute:": "🖖", ":ok_hand:": "👌", ":pinching_hand:": "🤏",
    ":v:": "✌️", ":crossed_fingers:": "🤞", ":love_you_gesture:": "🤟", ":metal:": "🤘", ":call_me_hand:": "🤙", ":point_left:": "👈", ":point_right:": "👉", ":point_up_2:": "👆",
    ":point_down:": "👇", ":point_up:": "☝️", ":raised_fist:": "✊", ":fist:": "👊", ":left_facing_fist:": "🤛", ":right_facing_fist:": "🤜", ":clap:": "👏", ":raised_hands:": "🙌",
    ":open_hands:": "👐", ":handshake:": "🤝", ":thumbsup:": "👍", ":thumbsdown:": "👎", ":pray:": "🙏", ":muscle:": "💪", ":foot:": "🦶", ":leg:": "🦵", ":brain:": "🧠",
    ":tooth:": "🦷", ":bone:": "🦴", ":eyes:": "👀", ":eye:": "👁️", ":ear:": "👂", ":nose:": "👃", ":lips:": "👄", ":tongue:": "👅", ":baby:": "👶", ":child:": "🧒",
    ":boy:": "👦",":girl:": "👧", ":adult:": "🧑", ":older_adult:": "🧓", ":man:": "👨", ":woman:": "👩", ":bearded_person:": "🧔", ":older_man:": "👴", ":older_woman:": "👵",
    ":monkey_face:": "🐵", ":monkey:": "🐒", ":dog:": "🐶", ":cat:": "🐱", ":mouse:": "🐭", ":hamster:": "🐹", ":rabbit:": "🐰", ":fox_face:": "🦊", ":bear:": "🐻",
    ":panda_face:": "🐼", ":koala:": "🐨", ":tiger:": "🐯", ":lion:": "🦁", ":cow:": "🐮", ":pig:": "🐷", ":frog:": "🐸", ":chicken:": "🐔", ":penguin:": "🐧", ":bird:": "🐦",
    ":baby_chick:": "🐤", ":duck:": "🦆", ":eagle:": "🦅", ":owl:": "🦉", ":bat:": "🦇", ":horse:": "🐴", ":unicorn:": "🦄", ":bee:": "🐝", ":bug:": "🐛", ":butterfly:": "🦋",
    ":snail:": "🐌", ":lady_beetle:": "🐞", ":ant:": "🐜", ":cricket:": "🦗", ":spider:": "🕷️", ":scorpion:": "🦂", ":turtle:": "🐢", ":snake:": "🐍", ":lizard:": "🦎",
    ":t_rex:": "🦖", ":sauropod:": "🦕", ":octopus:": "🐙", ":squid:": "🦑", ":shrimp:": "🦐", ":lobster:": "🦞", ":crab:": "🦀", ":blowfish:": "🐡", ":tropical_fish:": "🐠",
    ":fish:": "🐟", ":dolphin:": "🐬", ":whale:": "🐳", ":shark:": "🦈", ":crocodile:": "🐊", ":tiger2:": "🐅", ":leopard:": "🐆", ":zebra:": "🦓", ":gorilla:": "🦍",
    ":elephant:": "🐘", ":hippopotamus:": "🦛", ":mammoth:": "🦣", ":camel:": "🐪", ":two_hump_camel:": "🐫", ":giraffe:": "🦒", ":water_buffalo:": "🐃", ":ox:": "🐂", ":cow2:": "🐄",
    ":racehorse:": "🐎", ":pig2:": "🐖", ":ram:": "🐏", ":sheep:": "🐑", ":goat:": "🐐", ":deer:": "🦌", ":dog2:": "🐕", ":poodle:": "🐩", ":cat2:": "🐈", ":rooster:": "🐓",
    ":turkey:": "🦃",":dove:": "🕊️", ":rabbit2:": "🐇", ":mouse2:": "🐁", ":rat:": "🐀", ":chipmunk:": "🐿️", ":hedgehog:": "🦔", ":paw_prints:": "🐾", ":dragon:": "🐉",
    ":dragon_face:": "🐲", ":bouquet:": "💐", ":cherry_blossom:": "🌸", ":white_flower:": "💮", ":rosette:": "🏵️", ":rose:": "🌹", ":wilted_flower:": "🥀", ":hibiscus:": "🌺",
    ":sunflower:": "🌻", ":blossom:": "🌼", ":tulip:": "🌷", ":seedling:": "🌱", ":evergreen_tree:": "🌲", ":deciduous_tree:": "🌳", ":palm_tree:": "🌴", ":cactus:": "🌵",
    ":ear_of_rice:": "🌾", ":herb:": "🌿", ":shamrock:": "🍀", ":maple_leaf:": "🍁", ":fallen_leaf:": "🍂", ":leaves:": "🍃", ":mushroom:": "🍄", ":earth_africa:": "🌍",
    ":earth_americas:": "🌎", ":earth_asia:": "🌏", ":full_moon:": "🌕", ":waning_gibbous_moon:": "🌖", ":last_quarter_moon:": "🌗", ":waning_crescent_moon:": "🌘", ":new_moon:": "🌑",
    ":waxing_crescent_moon:": "🌒", ":first_quarter_moon:": "🌓", ":waxing_gibbous_moon:": "🌔", ":crescent_moon:": "🌙", ":star:": "⭐", ":sparkles:": "✨", ":sun:": "☀️",
    ":sunrise_over_mountains:": "🌄", ":sunrise:": "🌅", ":night_with_stars:": "🌃", ":milky_way:": "🌌", ":rainbow:": "🌈", ":bridge_at_night:": "🌉", ":water_wave:": "🌊",
    ":volcano:": "🌋", ":mount_fuji:": "🗻", ":camping:": "🏕️", ":beach_with_umbrella:": "🏖️", ":desert:": "🏜️", ":desert_island:": "🏝️", ":national_park:": "🏞️", ":stadium:": "🏟️",
    ":classical_building:": "🏛️", ":building_construction:": "🏗️", ":houses:": "🏘️", ":cityscape:": "🏙️", ":derelict_house:": "🏚️", ":house:": "🏠", ":house_with_garden:": "🏡",
    ":office:": "🏢", ":post_office:": "🏣", ":hospital:": "🏥", ":bank:": "🏦", ":hotel:": "🏨", ":love_hotel:": "🏩", ":convenience_store:": "🏪", ":school:": "🏫",
    ":department_store:": "🏬", ":factory:": "🏭", ":japanese_castle:": "🏯", ":european_castle:": "🏰", ":wedding:": "💒", ":tokyo_tower:": "🗼", ":statue_of_liberty:": "🗽",
    ":japan:": "🗾", ":moyai:": "🗿", ":sunrise_over_mountains:": "🌄", ":sunset:": "🌇", ":hotsprings:": "♨️", ":circus_carousel:": "🎠", ":ferris_wheel:": "🎡",
    ":roller_coaster:": "🎢", ":steam_locomotive:": "🚂", ":railway_car:": "🚃", ":high_speed_train:": "🚄", ":bullettrain_side:": "🚅", ":train2:": "🚆", ":metro:": "🚇",
    ":light_rail:": "🚈", ":station:": "🚉", ":tram:": "🚊", ":monorail:": "🚝", ":mountain_railway:": "🚞", ":canoe:": "🛶", ":sailboat:": "⛵", ":motor_boat:": "🛥️",
    ":passenger_ship:": "🛳️", ":ferry:": "⛴️", ":ship:": "🚢", ":airplane:": "✈️", ":small_airplane:": "🛩️", ":airplane_departure:": "🛫", ":airplane_arrival:": "🛬",
    ":rocket:": "🚀", ":flying_saucer:": "🛸", ":helicopter:": "🚁", ":cable_car:": "🚠", ":suspension_railway:": "🚟", ":satellite_orbital:": "🛰️", ":scooter:": "🛵",
    ":motorcycle:": "🏍️", ":racing_car:": "🏎️", ":oncoming_automobile:": "🚘", ":automobile:": "🚗", ":taxi:": "🚕", ":oncoming_taxi:": "🚖", ":articulated_lorry:": "🚛",
    ":truck:": "🚚", ":tractor:": "🚜", ":bike:": "🚲", ":kick_scooter:": "🛴", ":skateboard:": "🛹", ":auto_rickshaw:": "🛺", ":police_car_light:": "🚨", ":police_car:": "🚓",
    ":oncoming_police_car:": "🚔", ":ambulance:": "🚑", ":fire_engine:": "🚒", ":minibus:": "🚐", ":bus:": "🚌", ":oncoming_bus:": "🚍", ":trolleybus:": "🚎", 
    ":mountain_cableway:": "🚠", ":construction_site:": "🚧", ":stop_sign:": "🛑", ":railway_traffic_light:": "🚦", ":vertical_traffic_light:": "🚥", ":ship:": "🛳️",
    ":rocket:": "🚀", ":flying_saucer:": "🛸", ":world_map:": "🗺️", ":mountain:": "🏔️", ":volcano:": "🌋", ":beach_with_umbrella:": "🏖️", ":desert:": "🏜️", ":camping:": "🏕️",
    ":national_park:": "🏞️", ":stadium:": "🏟️", ":classical_building:": "🏛️", ":building_construction:": "🏗️", ":houses:": "🏘️", ":cityscape:": "🏙️", ":derelict_house:": "🏚️"
    }

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

def apply_theme(window, text_area=None, entry_widget=None, buttons=None, text=None):
    theme = THEMES[current_theme]
    window.configure(bg=theme["bg"])
    if text_area is not None:
        for t in text_area:
            t.configure(bg=theme["bg"], fg=theme["fg"])
    if entry_widget is not None:
        for entry in entry_widget:
            entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"])
    if buttons is not None:
        for button in buttons:
            button.configure(bg=theme["entry_bg"], fg=theme["entry_fg"])
    if text is not None:
        for txt in text:
            txt.configure(bg=theme["bg"], fg=theme["fg"])

def open_theme_selector(window, text_area, entry_widget, buttons):
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

    # Initialize list to hold theme buttons
    theme_buttons = []
    # Add the theme buttons to the button_frame
    for theme in THEMES.keys():
        if theme != "Selected_theme":
            theme_button = tk.Button(button_frame, text=theme, command=lambda t=theme: set_theme(t, window, text_area, entry_widget, buttons))
            theme_button.pack(pady=5)
            theme_buttons.append(theme_button)  # Append to the list

    # Add the custom theme, export, and import buttons
    create_button = tk.Button(button_frame, text="Create Custom Theme", command=lambda: create_custom_theme(window, text_area, entry_widget, buttons))
    create_button.pack(pady=5)
    export_button = tk.Button(button_frame, text="Export Themes", command=export_themes)
    export_button.pack(pady=5)
    import_button = tk.Button(button_frame, text="Import Themes", command=lambda: import_themes(window, text_area, entry_widget, buttons))
    import_button.pack(pady=5)

    # Update the scroll region of the canvas after adding buttons
    button_frame.update_idletasks()  # Ensure frame size is updated before setting scroll region
    canvas.config(scrollregion=canvas.bbox("all"))  # Set the scroll region to the bounds of all items in the canvas

    # Configure grid row and column weights to allow resizing
    theme_window.grid_rowconfigure(0, weight=1)  # Allow row 0 (Canvas) to expand
    theme_window.grid_columnconfigure(0, weight=1)  # Allow column 0 (Canvas) to expand

    # Apply the theme to the theme_window and buttons
    apply_theme(canvas, buttons=[*theme_buttons, create_button, export_button, import_button])

def set_theme(theme, window, text_area, entry_widget, buttons):
    global current_theme
    THEMES["Selected_theme"] = theme
    current_theme = theme
    save_themes()
    apply_theme(window, text_area=[text_area], entry_widget=[entry_widget], buttons=[*buttons])
    if current_theme_window:
        open_theme_selector(window, text_area, entry_widget, buttons) #updates theme selector.

def create_custom_theme(window, text_area, entry_widget, send_button):
    custom_window = Toplevel(window)
    custom_window.title("Create Custom Theme")
    custom_window.geometry("300x250")

    name_label = tk.Label(custom_window, text="Theme Name:")
    name_label.grid(row=0, column=0, sticky="w")
    name_entry = tk.Entry(custom_window)
    name_entry.grid(row=0, column=1)

    bg_label = tk.Label(custom_window, text="Background Color:")
    bg_label.grid(row=1, column=0, sticky="w")
    bg_button = tk.Button(custom_window, text="Select Color", command=lambda: choose_color(custom_window, "bg", bg_button))
    bg_button.grid(row=1, column=1)

    fg_label = tk.Label(custom_window, text="Foreground Color:")
    fg_label.grid(row=2, column=0, sticky="w")
    fg_button = tk.Button(custom_window, text="Select Color", command=lambda: choose_color(custom_window, "fg", fg_button))
    fg_button.grid(row=2, column=1)

    entry_bg_label = tk.Label(custom_window, text="Entry Background Color:")
    entry_bg_label.grid(row=3, column=0, sticky="w")
    entry_bg_button = tk.Button(custom_window, text="Select Color", command=lambda: choose_color(custom_window, "entry_bg", entry_bg_button))
    entry_bg_button.grid(row=3, column=1)

    entry_fg_label = tk.Label(custom_window, text="Entry Foreground Color:")
    entry_fg_label.grid(row=4, column=0, sticky="w")
    entry_fg_button = tk.Button(custom_window, text="Select Color", command=lambda: choose_color(custom_window, "entry_fg", entry_fg_button))
    entry_fg_button.grid(row=4, column=1)

    save_button = tk.Button(custom_window, text="Save Theme", command=lambda: save_custom_theme(custom_window, name_entry.get(), bg_button["bg"], fg_button["fg"], entry_bg_button["bg"], entry_fg_button["fg"], window, text_area, entry_widget, send_button))
    save_button.grid(row=5, column=0, columnspan=2, pady=10)

    apply_theme(custom_window, buttons=[bg_button, fg_button, entry_bg_button, entry_fg_button, save_button], entry_widget=[name_entry], text=[name_label, bg_label, fg_label, entry_bg_label, entry_fg_label])

def choose_color(window, color_type, button):
    color = colorchooser.askcolor()[1]
    if color:
        button.config(bg=color, fg="black") # sets the button background to the selected color
        window.update_idletasks() # update the window to show color change right away

def save_custom_theme(custom_window, name, bg, fg, entry_bg, entry_fg, window, text_area, entry_widget, send_button):
    if name and bg and fg and entry_bg and entry_fg:
        THEMES[name] = {"bg": bg, "fg": fg, "entry_bg": entry_bg, "entry_fg": entry_fg}
        save_themes()
        set_theme(name, window, text_area, entry_widget, send_button)
        custom_window.destroy()
        open_theme_selector(window, text_area, entry_widget, send_button)
    else:
        tk.messagebox.showerror("Error", "Please fill in all fields.")

def export_themes():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "w") as file:
            json.dump(THEMES, file, indent=4)

def import_themes(window, text_area, entry_widget, buttons):
    global THEMES, current_theme_window
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, "r") as file:
            imported_themes = json.load(file)
            imported_themes.pop("Selected_theme", None)     
            THEMES.update(imported_themes)
            save_themes()
            
            # Reapply the current theme after importing new themes
            apply_theme(window, text_area, entry_widget, [*buttons])

            # Close the old theme selector window if it exists
            if current_theme_window:
                current_theme_window.destroy()

            # Open the theme selector again with the updated list
            open_theme_selector(window, text_area, entry_widget, buttons)

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
def receive_messages(client_socket, text_area, window):
    global receive_thread
    while True:
        try:
            ready_to_read, _, _ = select.select([client_socket], [], [], 0.1)
            if ready_to_read:
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("Connection closed by the server")
                    window.destroy()
                    break

                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')
                
                if username == "FILE":
                    try:
                        filename_header = b''
                        while len(filename_header) < FILE_HEADER_LENGTH:
                            part = client_socket.recv(FILE_HEADER_LENGTH - len(filename_header))
                            if not part:
                                raise ConnectionError("Connection closed while receiving filename header")
                            filename_header += part
                        filename_length = int(filename_header.decode('utf-8').strip())

                        filename = client_socket.recv(filename_length).decode('utf-8')

                        file_data_header = b''
                        while len(file_data_header) < HEADER_LENGTH:
                            part = client_socket.recv(HEADER_LENGTH - len(file_data_header))
                            if not part:
                                raise ConnectionError("Connection closed while receiving file data header")
                            file_data_header += part
                        file_data_length = int(file_data_header.decode('utf-8').strip())

                        file_data = b''
                        while len(file_data) < file_data_length:
                            part = client_socket.recv(file_data_length - len(file_data))
                            if not part:
                                raise ConnectionError("Connection closed while receiving file data")
                            file_data += part
                        
                        username_header = client_socket.recv(HEADER_LENGTH)
                        username_length = int(username_header.decode('utf-8').strip())
                        username = client_socket.recv(username_length).decode('utf-8')
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            try:
                                image_data = io.BytesIO(file_data)
                                img = Image.open(image_data)
                                img.thumbnail((200, 200))
                                photo = ImageTk.PhotoImage(img)

                                local_time = time.strftime("%H:%M")
                                text_area.config(state=tk.NORMAL)
                                text_area.image_names = []
                                text_area.image_names.append(photo)
                                text_area.insert(tk.END, f"\n{local_time} {username} > ")
                                text_area.image_create(tk.END, image=photo)
                                text_area.yview(tk.END)
                                text_area.config(state=tk.DISABLED)
                            except Exception as e:
                                print(f"Error displaying image: {e}")
                                save_file(file_data, filename)
                                local_time = time.strftime("%H:%M")
                                text_area.config(state=tk.NORMAL)
                                text_area.insert(tk.END, f"\n{local_time} {username} > File received: {filename}")
                                text_area.yview(tk.END)
                                text_area.config(state=tk.DISABLED)
                        else:
                            save_file(file_data, filename)
                            local_time = time.strftime("%H:%M")
                            text_area.config(state=tk.NORMAL)
                            text_area.insert(tk.END, f"\n{local_time} {username} > File received: {filename}")
                            text_area.yview(tk.END)
                            text_area.config(state=tk.DISABLED)

                        continue # Important: Skip regular message processing after file
                    except ValueError as e:
                        print(f"Error processing file header: {e}")
                        continue
                    except Exception as e:
                        print(f"Error receiving file: {e}")
                        continue
                else:
                    message_header = client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = client_socket.recv(message_length)
                    message_str = message.decode('utf-8')
                    local_time = time.strftime("%H:%M")
                    text_area.config(state=tk.NORMAL)
                    text_area.insert(tk.END, f"\n{local_time} {username} > {message_str}")
                    text_area.yview(tk.END)
                    text_area.config(state=tk.DISABLED)

        except BlockingIOError:
            continue
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def display_image(text_area, photo, username):
    local_time = time.strftime("%H:%M")
    text_area.config(state=tk.NORMAL)
    if not hasattr(text_area, "image_names"):
        text_area.image_names = []
    text_area.image_names.append(photo)

def replace_emoji_shortcuts(message):
    global emojis
    for shortcut, emoji in emojis.items():
        message = message.replace(shortcut, emoji)
    return message

# Send messages from the GUI text box
def send_message(client_socket, entry_widget, text_area):
    message = entry_widget.get()
    if message:
        message = replace_emoji_shortcuts(message)
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

def send_file(client_socket, filename):
    try:
        with open(filename, 'rb') as file:
            file_data = file.read()

        filename_encoded = os.path.basename(filename).encode('utf-8')
        filename_length = len(filename_encoded)
        filename_header = f"{filename_length:<{FILE_HEADER_LENGTH}}".encode('utf-8')

        file_data_length = len(file_data)
        file_data_header = f"{file_data_length:<{HEADER_LENGTH}}".encode('utf-8')

        # Send a file indicator
        file_indicator = "FILE".encode('utf-8')
        indicator_header = f"{len(file_indicator):<{HEADER_LENGTH}}".encode('utf-8')

        #send the file indicator, then the file name length, then the filename, then the file data length, then the data.
        client_socket.send(indicator_header + file_indicator + filename_header + filename_encoded + file_data_header + file_data)

    except Exception as e:
        print(f"Error sending file: {e}")

def select_file_and_send(client_socket, text_area):
    filename = filedialog.askopenfilename()
    if filename:
        send_file(client_socket, filename)
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, f"\nYou > File sent: {os.path.basename(filename)}")
        text_area.yview(tk.END)
        text_area.config(state=tk.DISABLED)

def save_file(file_data, filename):
    try:
        # Create the 'received_files' folder if it doesn't exist
        if not os.path.exists("received_files"):
            os.makedirs("received_files")

        # Construct the full file path
        file_path = os.path.join("received_files", filename)

        # Save the file
        with open(file_path, 'wb') as file:
            file.write(file_data)
        print(f"File saved as {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

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

    ip_text = tk.Label(root, text="IP Address:")
    ip_text.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    ip_entry = tk.Entry(root, width=30)  # Assign to global variable
    ip_entry.grid(row=0, column=1, padx=5, pady=5)

    port_text = tk.Label(root, text="Port:")
    port_text.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    port_entry = tk.Entry(root, width=30)  # Assign to global variable
    port_entry.grid(row=1, column=1, padx=5, pady=5)

    user_text = tk.Label(root, text="Username:")
    user_text.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    username_entry = tk.Entry(root, width=30)  # Assign to global variable
    username_entry.grid(row=2, column=1, padx=5, pady=5)

    error_label = tk.Label(root, text="", fg="red")
    error_label.grid(row=5, column=0, columnspan=2)

    connect_button = tk.Button(root, text="Connect", command=lambda: try_connect(ip_entry, port_entry, username_entry, error_label, root))
    connect_button.grid(row=3, column=0, columnspan=2, pady=10)

    prev_connections_button = tk.Button(root, text="Previous Connections", command=lambda: open_previous_connections(root))
    prev_connections_button.grid(row=4, column=0, columnspan=2, pady=5)

    apply_theme(root, entry_widget=[ip_entry, port_entry, username_entry], buttons=[connect_button, prev_connections_button, error_label], text=[ip_text, port_text, user_text])

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

    apply_theme(prev_window, entry_widget=[server_listbox], buttons=[join_button, add_button, edit_button])

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

def emoji_lookup(input_field):
    global emojis

    emoji_window = tk.Toplevel()
    emoji_window.title("Emoji Lookup")

    emoji_frame = tk.Frame(emoji_window)
    emoji_frame.pack()

    row_num = 0
    col_num = 0
    emoji_count = 0
    for shortcut, emoji in emojis.items():
        button = tk.Button(emoji_frame, text=emoji, command=lambda e=emoji: add_emoji(e, input_field), font=("Arial", 16), width=5)
        button.grid(row=row_num, column=col_num, padx=1, pady=1)
        col_num += 1
        if col_num >= 20:
            col_num = 0
            row_num += 1
        emoji_count += 1
    
    print(emoji_count)
        
    
    apply_theme(emoji_window, buttons=emoji_frame.winfo_children())

def add_emoji(emoji, input_field):
    input_field.insert(tk.END, emoji)

# Create the Tkinter window and its components
def create_gui(client_socket):
    global receive_thread
    window = tk.Tk()
    window.title("Chat Client")
    
    # Create message display box
    text_area = scrolledtext.ScrolledText(window, width=50, height=15, wrap=tk.WORD, state=tk.DISABLED)
    text_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Create message entry box
    entry_widget = tk.Entry(window, width=40)
    entry_widget.grid(row=1, column=0, padx=10, pady=10)

    # Create send file button
    file_button = tk.Button(window, text="Send File", width=10, command=lambda: select_file_and_send(client_socket, text_area))
    file_button.grid(row=1, column=1, columnspan=2, pady=5)
    
    # Create emoji button
    emoji_button = tk.Button(window, text="Emoji", width=10, command=lambda: emoji_lookup(entry_widget))
    emoji_button.grid(row=2, column=1, columnspan=2, pady=5)

    # Bind Enter key to send message
    entry_widget.bind('<Return>', lambda event: send_message(client_socket, entry_widget, text_area))

    # Start receiving messages in a separate thread
    theme_button = tk.Button(window, text="Change Theme", command=lambda: open_theme_selector(window, text_area, entry_widget, [file_button, theme_button, emoji_button]))
    theme_button.grid(row=2, column=0, columnspan=2, pady=5)

    apply_theme(window, text_area=[text_area], entry_widget=[entry_widget], buttons=[file_button, theme_button, emoji_button])
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, text_area, window), daemon=True)
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
