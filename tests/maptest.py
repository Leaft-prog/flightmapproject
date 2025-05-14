from tkinter import *
from PIL import Image, ImageTk
import tkintermapview
import socket
import struct
import json
import threading

root = Tk()
root.title('IFEMAP')
root.geometry("900x700")

multicast_group = '224.0.0.1'  # Multicast address
multicast_port = 5004          # Multicast port

llong = None
llat = None

# Function to listen for multicast messages
def listen_for_multicast():
    global llong
    global llat
    global first_start
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Bind the socket to the address and port
    sock.bind(('', multicast_port))

    # Tell the socket to join the multicast group
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        # Receive message from multicast group
        data, _ = sock.recvfrom(1024)

        try:
            # Parse the JSON data received
            json_data = json.loads(data.decode('utf-8'))

            # Extract the latitude and longitude
            lat = json_data.get("local-latitude", None)
            lon = json_data.get("local-longitude", None)

            # If both lat and lon are present, update the map
            if lat is not None and lon is not None:
                llat = lat
                llong = lon
                # Make sure to update the map in the main thread
                root.after(0, updatemap)
        except Exception as e:
            print(f"Error parsing data: {e}")
            root.after(0, show_error)

# Function to update the map with the new coordinates
def updatemap():
    global llong
    global llat
    if llong is not None and llat is not None:
        map_widget.set_position(llong, llat)
        map_widget.set_marker(llong, llat, icon=aircraft_icon)

# Function to show error message if data is invalid
def show_error():
    error_text.pack()

# Function to start the multicast listener in a separate thread
def receiver_thread():
    multicast_thread = threading.Thread(target=listen_for_multicast, daemon=True)
    multicast_thread.start()

# Set up the Tkinter GUI
my_label = LabelFrame(root)
my_label.pack(pady=20)

map_widget = tkintermapview.TkinterMapView(my_label, width=800, height=600, corner_radius=0)

# Set A Zoom Level
map_widget.set_zoom(5)

error_text = Label(root, text="Unable to retrieve flight data")

# Load the aircraft icon
aircraft_icon_path_og = Image.open("./resources/aircraft.png")  # Path to your marker icon image
aircraft_icon_resize = aircraft_icon_path_og.resize((50, 50))
aircraft_icon_rotation = aircraft_icon_resize.rotate(0, expand=True)
aircraft_icon = ImageTk.PhotoImage(aircraft_icon_rotation)

map_widget.pack()

# Start the multicast listener in a separate thread
if __name__ == "__main__":
    receiver_thread()
    root.mainloop()
