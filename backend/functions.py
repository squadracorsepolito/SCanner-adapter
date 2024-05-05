# FUNCTIONS
import cantools
import socket
import threading
import json
import time
import subprocess
import ctypes
from cannellonipy.cannellonipy import run_cannellonipy, CannelloniHandle

# Constants
LOCALHOST_IP = "127.0.0.1"
BUFFER_SIZE = 1024

# Controller
def start_connection_controller(IP_SCANNER, CAN0_PORT, CAN1_PORT, UDP_PORT, PATH_DBC_CAN0, PATH_DBC_CAN1, label_connected, connect_button):
    udp_socket = open_stream_udp(int(UDP_PORT))
    cannelloni_sockets = open_stream_cannelloni(IP_SCANNER, CAN0_PORT, CAN1_PORT)
    time.sleep(1)

    if udp_socket and cannelloni_sockets[0].udp_pcb and cannelloni_sockets[1].udp_pcb: 
        print("Connection established")
        read_data_cannelloni(udp_socket, cannelloni_sockets, PATH_DBC_CAN0, PATH_DBC_CAN1, UDP_PORT)
        label_connected.pack()
        connect_button.config(state="disabled")
    else:
        print("Connection failed")

# Opens a stream from the specified scanner IP and ports
def open_stream_cannelloni(IP_SCANNER, CAN0_PORT, CAN1_PORT):
    try:
        # Create a cannellonipy handle
        cannellonipy_handle0 = CannelloniHandle()
        cannellonipy_handle1 = CannelloniHandle()

        # Run the library on the specified SCanner ports
        cannelloni_thread0 = threading.Thread(target=run_cannellonipy, args=(cannellonipy_handle0, IP_SCANNER, CAN0_PORT), daemon=True)
        cannelloni_thread0.start()
        time.sleep(1)
        cannelloni_thread1 = threading.Thread(target=run_cannellonipy, args=(cannellonipy_handle1, IP_SCANNER, CAN1_PORT), daemon=True)
        cannelloni_thread1.start()

        return cannellonipy_handle0, cannellonipy_handle1

    except Exception as e:
        print(f"Error opening stream from SCanner board: {e}")
    
# Opens a UDP streaming server for PlotJuggler on the specified port
def open_stream_udp(UDP_PORT):
    try:
        # Create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if server_socket:
            print(f"UDP JSON server is active on port {UDP_PORT}")
        return server_socket

    except Exception as e:
        print(f"Error opening UDP streaming server: {e}")

# Stream JSON data to PlotJuggler via UDP
def send_stream_to_plotjuggler(udp_socket, json_data, UDP_PORT):
    try:
        print(f"Sending JSON data: {json_data}")
        # Serialize the JSON data to a string
        json_string = json.dumps(json_data)
        # Encode the JSON string to bytes
        json_bytes = json_string.encode('utf-8')
        # Send JSON data to the server
        udp_socket.sendto(json_bytes, (LOCALHOST_IP, int(UDP_PORT)))    # Check with cmd:  nc -ul <UDP_PORT>

    except Exception as e:
        print(f"Error sending data via UDP: {e}")

# Read data from the SCanner via cannelloni
def read_data_cannelloni(udp_socket, cannelloni_sockets, PATH_DBC_CAN0, PATH_DBC_CAN1, UDP_PORT):
    try:
        while True:
            # Get the received frames form cannelloni
            received_frames_can0 = cannelloni_sockets[0].get_received_can_frames()
            received_frames_can1 = cannelloni_sockets[1].get_received_can_frames()

            # Convert Cannelloni data to JSON
            json_data0 = cannelloni_to_json(received_frames_can0, PATH_DBC_CAN0)
            json_data1 = cannelloni_to_json(received_frames_can1, PATH_DBC_CAN1)

            # Merge the two JSON objects streams
            if json_data0 and json_data1:
                json_data = {**json_data0, **json_data1}
                print(json_data)
                # Send the JSON data to PlotJuggler via UDP
                send_stream_to_plotjuggler(udp_socket, json_data, UDP_PORT)
            else:
                print("No data received")
                return

    except Exception as e:
        print(f"Error reading data from SCanner: {e}")

# Cannelloni CAN stream to JSON converter
def cannelloni_to_json(frame_cannelloni, dbc_path):
    try:
        # Load DBC file
        if dbc_path == "Path":
            print("No DBC file provided")
            return None
        else:
            dbc = cantools.db.load_file(dbc_path)
        
        # Initialize empty JSON object
        json_data = {}
        
        # Iterate over CAN frames in the data section
        for _ in range(count):
            # Parse CAN frame
            can_id = (frame_cannelloni[offset] << 24) | (frame_cannelloni[offset + 1] << 16) | \
                    (frame_cannelloni[offset + 2] << 8) | frame_cannelloni[offset + 3]
            length = frame_cannelloni[offset + 4]
            flags = frame_cannelloni[offset + 5] if length & 0x80 else None
            data_start = offset + 6 if length & 0x80 else offset + 5
            
            # Extract data bytes
            data = frame_cannelloni[data_start:data_start + length]
            
            # Decode CAN frame using DBC file
            frame_decoded = dbc.decode_message(can_id, data)
            
            # Add decoded CAN frame to JSON object
            json_data[str(can_id)] = frame_decoded
            
            # Update offset for the next CAN frame
            offset = data_start + length
            
        return json.dumps(json_data, indent=4)
    except Exception as e:
        print(f"Error converting Cannelloni data to JSON: {e}")
        


# CANNELLONI DATA FORMAT
# ## Data Frames
# Each data frame can contain several CAN frames.
# The header of a data frame contains the following
# information:

# | Bytes |  Name   |   Description       |
# |-------|---------|---------------------|
# |   1   | Version | Protocol Version    |
# |   1   | OP Code | Type of Frame (DATA)|
# |   1   | Seq No  | Sequence number     |
# |   2   | Count   | Number of CAN Frames|

# After the header, the data section follows.
# Each CAN frame has the following format which
# is similar to `canfd_frame` defined in `<linux/can.h>`.

# | Bytes |  Name   |   Description       |
# |-------|---------|---------------------|
# |   4   |  can_id |  see `<linux/can.h>`|
# |   1   |  len    |  size of payload/dlc|
# |   1   |  flags^ |  CAN FD flags       |
# |0-8/64 |  data   |  Data section       |

# ^ = CAN FD only
# Everything is Big-Endian/Network Byte Order.
# *The frame format is identical for UDP and SCTP*

# ## CAN FD
# CAN FD frames are marked with the MSB of `len` being
# set, so `len | (0x80)`. If this bit is set, the `flags`
# attribute is inserted between `len` and `data`.
# For CAN 2.0 frames this attribute is missing.
# `data` can be 0-8 Bytes long for CAN 2.0 and 0-64 Bytes
# for CAN FD frames.