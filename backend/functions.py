# FUNCTIONS
import cantools
import socket
import threading

# Constants
LOCALHOST_IP = "127.0.0.1"

# Opens a cannelloni stream from SCanner board on the specified port
def open_stream_cannelloni(scanner_ip, port1, port2):
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
    
# Opens a cannelloni stream from CAN1 on the specified port
def open_stream_plotjuggler(port):
    return True

# Cannelloni CAN stream to JSON converter
def cannelloni_to_json(stream_cannelloni):
    return json