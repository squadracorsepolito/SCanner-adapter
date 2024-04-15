# FUNCTIONS
import cantools
import socket
import threading
import json
import time

# Constants
LOCALHOST_IP = "127.0.0.1"

# Opens a stream from the specified scanner IP and ports
def open_stream_cannelloni(scanner_ip, port1, port2):
    # NON VA BENE PERCHè LO STREAM DEVE ESSERE APERTO CON CANNELLONI (?)
    try:
        # Create IPv4 TCP/IP sockets for both scanners
        scanner_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        scanner_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the CAN0 and CAN1
        scanner_socket1.connect((scanner_ip, port1))
        scanner_socket2.connect((scanner_ip, port2))
        
        # List to store merged data from both streams
        merged_cannelloni_stream = []
        
        # Function to handle data from each scanner and merge into the list
        def handle_scanner(scanner_socket):
            while True:
                data = scanner_socket.recv(1024)
                if not data:
                    break
                # Process the received data or merge it into the single stream
                merged_cannelloni_stream.append(data.decode())  # Example: Append the received data
        
        # Create threads to handle each scanner's stream
        thread1 = threading.Thread(target=handle_scanner, args=(scanner_socket1,))
        thread2 = threading.Thread(target=handle_scanner, args=(scanner_socket2,))
        
        # Start the threads
        thread1.start()
        thread2.start()
        
        # Wait for threads to finish
        thread1.join()
        thread2.join()
        
        # Return the merged data
        return merged_cannelloni_stream
        
    except Exception as e:
        print(f"Error opening stream from SCanner board: {e}")
    finally:
        # Close sockets
        scanner_socket1.close()
        scanner_socket2.close()
    
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
                    server_socket.sendto(json_str.encode(), ("0.0.0.0", port))   # Check with cmd:  nc -ul 9870

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
    dbc = cantools.db.load_file(dbc_path)
    message_decoded = dbc.decode_message(message_cannelloni.arbitration_id, message_cannelloni.data)
    
    # TO DO 

    return json
