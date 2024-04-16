# FUNCTIONS
import cantools
import socket
import threading
import json
import time
import subprocess
import ctypes

# Constants
LOCALHOST_IP = "127.0.0.1"

# Opens a stream from the specified scanner IP and ports
def open_stream_cannelloni(scanner_ip, port1, port2):
    try:
        cannelloni = ctypes.CDLL("cannelloni_ports/main_cannelloni.so")  
        # To recompile the library use (inside the cannelloni folder): gcc -shared -o cannelloni.so -fPIC main_cannelloni.c

        cannelloni.init()
        cannelloni.open_stream(scanner_ip.encode(), int(port1), int(port2))
        
    except Exception as e:
        print(f"Error opening stream from SCanner board: {e}")
    
# Opens a JSON streaming server for PlotJuggler on the specified port
def open_stream_plotjuggler(port):
    try:
        # Create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        # server_socket.bind((LOCALHOST_IP, port))

        print(f"JSON streaming server for PlotJuggler is listening on port {port}")

        def handle_client():
            try:
                while True:
                    # Generate JSON data (replace with your actual data)
                    example_json_data = {'Engine_Speed': 0, 'Inlet_Manifold_Pressure': 97.6, 'Inlet_Air_Temperature': 32, 'Throttle_Position': 17.3}
                    print(f"Sending JSON data to port {port}: {example_json_data}")
                    
                    # Convert JSON data to string
                    json_str = json.dumps(example_json_data)

                    # Send JSON data to the client
                    server_socket.sendto(json_str.encode(), (LOCALHOST_IP, port))   # Check with cmd:  nc -ul 9870

                    time.sleep(1)
            except Exception as e:
                print(f"Error handling client connection: {e}")

        # Start the thread to handle PlotJuggler connections
        stream_plotjuggler_thread = threading.Thread(target=handle_client, daemon=True)
        stream_plotjuggler_thread.start()

    except Exception as e:
        print(f"Error opening JSON streaming server: {e}")

# Cannelloni CAN stream to JSON converter
def cannelloni_to_json(message_cannelloni, dbc_path):
    # Load DBC file
    dbc = cantools.db.load_file(dbc_path)
    
    # Initialize empty JSON object
    json_data = {}
    
    # Parse header of the frame
    version = message_cannelloni[0]
    op_code = message_cannelloni[1]
    seq_no = message_cannelloni[2]
    count = (message_cannelloni[3] << 8) | message_cannelloni[4]
    
    # Iterate over CAN frames in the data section
    offset = 5  # Start of data section
    for _ in range(count):
        # Parse CAN frame
        can_id = (message_cannelloni[offset] << 24) | (message_cannelloni[offset + 1] << 16) | \
                 (message_cannelloni[offset + 2] << 8) | message_cannelloni[offset + 3]
        length = message_cannelloni[offset + 4]
        flags = message_cannelloni[offset + 5] if length & 0x80 else None
        data_start = offset + 6 if length & 0x80 else offset + 5
        
        # Extract data bytes
        data = message_cannelloni[data_start:data_start + length]
        
        # Decode CAN frame using DBC file
        frame_decoded = dbc.decode_message(can_id, data)
        
        # Add decoded CAN frame to JSON object
        json_data[str(can_id)] = frame_decoded
        
        # Update offset for the next CAN frame
        offset = data_start + length
        
    return json.dumps(json_data, indent=4)


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