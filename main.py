import tkinter as tk
from tkinter import filedialog, StringVar, OptionMenu
from backend.functions import start_connection_controller, disconnect
import threading
import time
import argparse

class GUI:
    def __init__(self, config_path=None, mode=None, direct_connect=False):
        # Config parameters with default values
        self.MODE = "Select"
        self.PATH_CONFIG_MODEL = "Path"
        self.PATH_DBC_CAN0 = "Path"
        self.PATH_DBC_CAN1 = "Path"
        self.UDP_PORT = 9870
        self.IP_SCANNER = "0.0.0.0"
        self.CAN0_PORT = 4000
        self.CAN1_PORT = 5000
        self.CAN_SOCKET0 = "vcan0"
        self.CAN_SOCKET1 = "vcan1"

        global controller_thread
        controller_thread = None
        self.connect_button = None
        self.label_connected = None
        self.label_connected = None
        self.disconnect_button = None

        # Load configuration if a path was provided
        if config_path:
            self.PATH_CONFIG_MODEL = config_path
            self.startup()

        if mode:
            self.MODE = mode

        if direct_connect:
            self.connect_thread(direct=True)
            return

        # Create a new instance of Tkinter application
        self.app = tk.Tk()

    # ---------- WINDOW SETTINGS ---------------------------------------
        self.app.title("SCanner Adapter")

        # Set the width and height of the window
        self.screen_width = self.app.winfo_screenwidth()
        self.screen_height = self.app.winfo_screenheight()
        self.window_width = 500
        self.window_height = 700
        self.x_coordinate = (self.screen_width - self.window_width) // 2
        self.y_coordinate = (self.screen_height - self.window_height) // 2

        # Set the geometry of the window to position it on the center of the screen
        self.app.geometry(f"{self.window_width}x{self.window_height}+{self.x_coordinate}+{self.y_coordinate}")
        self.frame = tk.Frame(self.app)
        self.frame.pack(pady=20)

    # ---------- GUI ELEMENTS --------------------------------------------
        self.label = tk.Label(self.frame, text="Hello, this is the SCanner Adapter! \nYou have to enter all the required values on the form below \n and than press connect!")
        self.label.grid(row=0, column=1, columnspan=10, pady=10)

        # Functioning mode
        self.label_mode = tk.Label(self.frame, text="Select functioning mode to use (PhysicalCAN is Linux only):")
        self.label_mode.grid(row=1, column=1, columnspan=10)
        options = ["Select", "Cannelloni", "PhysicalCAN"]  # Update the naming in the backend if modified
        self.selected_option = StringVar()
        # Set the provided mode if any
        if mode:
            self.selected_option.set(mode)
            self.update_ui_based_on_mode(mode)
        else:
            self.selected_option.set(options[0])
        self.dropdown = OptionMenu(self.frame, self.selected_option, *options, command=self.update_ui_based_on_mode)
        self.dropdown.grid(row=2, column=1, columnspan=10, pady=10)

        # Path to CONFIG
        self.label_path_config_model = tk.Label(self.frame, text="Select path to CONFIG model to use:")
        self.label_path_config_model.grid(row=3, column=1, columnspan=10)
        self.textbox_path_config_model = tk.Text(self.frame, height=1, width=50)
        self.textbox_path_config_model.grid(row=4, column=1, columnspan=10)
        self.textbox_path_config_model.insert("1.0", self.PATH_CONFIG_MODEL)
        self.browse_button_config_model = tk.Button(self.frame, text="Browse", command=self.browse_file_config_model)
        self.browse_button_config_model.grid(row=5, column=1, columnspan=10, pady=10)

        # Local port JSON relay
        self.label_udp_port = tk.Label(self.frame, text="Local port JSON UDP server (for PlotJuggler):")
        self.label_udp_port.grid(row=12, column=1, columnspan=10)
        self.textbox_udp_port = tk.Text(self.frame, height=1, width=30)
        self.textbox_udp_port.insert("1.0", self.UDP_PORT)                       
        self.textbox_udp_port.grid(row=13, column=1, columnspan=10)

        # Path dbc CAN0
        self.label_path_dbc_can0 = tk.Label(self.frame, text="Select path to CAN0 DBC:")
        self.label_path_dbc_can0.grid(row=14, column=1, columnspan=10)
        self.textbox_path_dbc_can0 = tk.Text(self.frame, height=1, width=50)
        self.textbox_path_dbc_can0.grid(row=15, column=1, columnspan=10)
        self.textbox_path_dbc_can0.insert("1.0", self.PATH_DBC_CAN0)
        self.browse_button_can0 = tk.Button(self.frame, text="Browse", command=self.browse_file_can0)
        self.browse_button_can0.grid(row=16, column=1, columnspan=10)

        # Path dbc CAN1
        self.label_path_dbc_can1 = tk.Label(self.frame, text="Select path to CAN1 DBC:")
        self.label_path_dbc_can1.grid(row=17, column=1, columnspan=10)
        self.textbox_path_dbc_can1 = tk.Text(self.frame, height=1, width=50)
        self.textbox_path_dbc_can1.grid(row=18, column=1, columnspan=10)
        self.textbox_path_dbc_can1.insert("1.0", self.PATH_DBC_CAN1)
        self.browse_button_can1 = tk.Button(self.frame, text="Browse", command=self.browse_file_can1)
        self.browse_button_can1.grid(row=19, column=1, columnspan=10)

        # Connect button
        self.connect_button = tk.Button(self.frame, text="Connect", command=self.connect_thread, font=("Arial", 14, "bold"), width=8, height=2)
        self.connect_button.grid(row=20, column=0, columnspan=5, pady=15)

        # Disconnect button
        self.disconnect_button = tk.Button(self.frame, text="Disconnect", command=self.disconnect, font=("Arial", 14, "bold"), width=8, height=2, state="disabled")
        self.disconnect_button.grid(row=20, column=7, columnspan=5, pady=15)

        # Connected status
        self.label_connected = tk.Label(self.frame, text="CONNECTED!", font=("Arial", 14, "bold"))
        self.label_connected.grid_forget()

        # Connected status
        self.label_config_loaded = tk.Label(self.frame, text="CONFIG loaded!", font=("Arial", 14, "bold"))
        self.label_config_loaded.grid_forget()

        # Start the Tkinter event loop
        self.app.mainloop()

    def update_ui_based_on_mode(self, selected_mode):
        # Clear existing widgets for dynamic content
        for widget in self.frame.grid_slaves(row=6):
            widget.grid_forget()
        for widget in self.frame.grid_slaves(row=7):
            widget.grid_forget()
        for widget in self.frame.grid_slaves(row=8):
            widget.grid_forget()
        for widget in self.frame.grid_slaves(row=9):
            widget.grid_forget()
        for widget in self.frame.grid_slaves(row=10):
            widget.grid_forget()
        for widget in self.frame.grid_slaves(row=11):
            widget.grid_forget()

        if selected_mode == "PhysicalCAN":
            # CAN Socket 1
            self.label_can_socket0 = tk.Label(self.frame, text="CAN0 socket:")
            self.label_can_socket0.grid(row=6, column=1, columnspan=10)
            self.textbox_can_socket0 = tk.Text(self.frame, height=1, width=30)
            self.textbox_can_socket0.insert("1.0", self.CAN_SOCKET0)               
            self.textbox_can_socket0.grid(row=7, column=1, columnspan=10)

            # CAN Socket 2
            self.label_can_socket1 = tk.Label(self.frame, text="CAN1 socket:")
            self.label_can_socket1.grid(row=8, column=1, columnspan=10)
            self.textbox_can_socket1 = tk.Text(self.frame, height=1, width=30)
            self.textbox_can_socket1.insert("1.0", self.CAN_SOCKET1)               
            self.textbox_can_socket1.grid(row=9, column=1, columnspan=10)
        elif selected_mode == "Cannelloni":
            # IP Scanner
            self.label_ip_scanner = tk.Label(self.frame, text="IP SCanner:")
            self.label_ip_scanner.grid(row=6, column=1, columnspan=10)
            self.textbox_ip_scanner = tk.Text(self.frame, height=1, width=30)
            self.textbox_ip_scanner.insert("1.0", self.IP_SCANNER)               
            self.textbox_ip_scanner.grid(row=7, column=1, columnspan=10)

            # CAN0 Port
            self.label_can0_port = tk.Label(self.frame, text="CAN0 port:")
            self.label_can0_port.grid(row=8, column=1, columnspan=10)
            self.textbox_can0_port = tk.Text(self.frame, height=1, width=30)
            self.textbox_can0_port.insert("1.0", self.CAN0_PORT)                        
            self.textbox_can0_port.grid(row=9, column=1, columnspan=10)

            # CAN1 Port
            self.label_can1_port = tk.Label(self.frame, text="CAN1 port:")
            self.label_can1_port.grid(row=10, column=1, columnspan=10)
            self.textbox_can1_port = tk.Text(self.frame, height=1, width=30)
            self.textbox_can1_port.insert("1.0", self.CAN1_PORT)                        
            self.textbox_can1_port.grid(row=11, column=1, columnspan=10)
        else:
            return

    # ---------- FUNCTIONS ---------------------------------------------
    def browse_file_config_model(self):
        global PATH_CONFIG_MODEL

        self.PATH_CONFIG_MODEL = filedialog.askopenfilename()
        self.textbox_path_config_model.delete("1.0", tk.END)
        self.textbox_path_config_model.insert("1.0", self.PATH_CONFIG_MODEL)

        self.label_config_loaded.grid(row=20, column=1, columnspan=10)
        self.startup()

    def browse_file_can0(self):
        self.PATH_DBC_CAN0 = filedialog.askopenfilename()
        self.textbox_path_dbc_can0.delete("1.0", tk.END)
        self.textbox_path_dbc_can0.insert("1.0", self.PATH_DBC_CAN0)

    def browse_file_can1(self):
        self.PATH_DBC_CAN1 = filedialog.askopenfilename()
        self.textbox_path_dbc_can1.delete("1.0", tk.END)
        self.textbox_path_dbc_can1.insert("1.0", self.PATH_DBC_CAN1)

    def connect_thread(self, direct=False):
        global controller_thread
        # Start a new thread for the connect function
        controller_thread = threading.Thread(target=self.connect, args=(direct,), daemon=True)
        controller_thread.start()

    def connect(self, direct=False):
        if not direct:
            # Get the content of each textbox widget
            if hasattr(self, 'textbox_ip_scanner'):
                self.IP_SCANNER = self.textbox_ip_scanner.get("1.0", "end-1c")
            if hasattr(self, 'textbox_can0_port'):
                self.CAN0_PORT = self.textbox_can0_port.get("1.0", "end-1c")
            if hasattr(self, 'textbox_can1_port'):
                self.CAN1_PORT = self.textbox_can1_port.get("1.0", "end-1c")
            if hasattr(self, 'textbox_can_socket0'):
                self.CAN_SOCKET0 = self.textbox_can_socket0.get("1.0", "end-1c")
            if hasattr(self, 'textbox_can_socket1'):
                self.CAN_SOCKET1 = self.textbox_can_socket1.get("1.0", "end-1c")
            self.UDP_PORT = self.textbox_udp_port.get("1.0", "end-1c")
            self.PATH_DBC_CAN0 = self.textbox_path_dbc_can0.get("1.0", "end-1c")
            self.PATH_DBC_CAN1 = self.textbox_path_dbc_can1.get("1.0", "end-1c")
            # Get the selected mode
            self.MODE = self.selected_option.get()
            # Save the paths to the CONFIG file for future reuse
            self.save_to_config_file() 

        try:
            print("Mode: ", self.MODE)
            if self.MODE != "Select":
                start_connection_controller(self.IP_SCANNER, self.CAN0_PORT, self.CAN1_PORT, self.UDP_PORT, 
                                            self.PATH_DBC_CAN0, self.PATH_DBC_CAN1, self.label_connected, 
                                        self.connect_button, self.disconnect_button, self.MODE, 
                                        self.CAN_SOCKET0, self.CAN_SOCKET1)
            else:
                print("Please select a valid mode")
                return
        except Exception as e:
            print(f"Connection failed: {e}")

    def disconnect(self):
        global controller_thread
        # Stop the controller thread if it's running
        if controller_thread:
            disconnect()
            time.sleep(1)
            controller_thread.join()
            self.connect_button.config(state="active")
            self.disconnect_button.config(state="disabled")
            self.label_connected.grid_forget()
            self.label_config_loaded.grid_forget()
            controller_thread = None
            print("Disconnected")
        else:
            return

    def startup(self):
        with open(self.PATH_CONFIG_MODEL, 'r') as f:
            for line in f:
                key, value = line.strip().split("=")
                if key == "PATH_DBC_CAN0":
                    self.PATH_DBC_CAN0 = value
                elif key == "PATH_DBC_CAN1":
                    self.PATH_DBC_CAN1 = value
                elif key == "UDP_PORT":
                    self.UDP_PORT = value
                elif key == "IP_SCANNER":
                    self.IP_SCANNER = value
                elif key == "CAN0_PORT":
                    self.CAN0_PORT = value
                elif key == "CAN1_PORT":
                    self.CAN1_PORT = value
                elif key == "CAN_SOCKET0":
                    self.CAN_SOCKET0 = value
                elif key == "CAN_SOCKET1":
                    self.CAN_SOCKET1 = value

        # Update the interface with new values
        self.update_interface()

    def update_interface(self):
        if hasattr(self, 'textbox_ip_scanner'):
            self.textbox_ip_scanner.delete("1.0", tk.END)
            self.textbox_ip_scanner.insert("1.0", self.IP_SCANNER)
        if hasattr(self, 'textbox_can0_port'):
            self.textbox_can0_port.delete("1.0", tk.END)
            self.textbox_can0_port.insert("1.0", self.CAN0_PORT)
        if hasattr(self, 'textbox_can1_port'):
            self.textbox_can1_port.delete("1.0", tk.END)
            self.textbox_can1_port.insert("1.0", self.CAN1_PORT)
        if hasattr(self, 'textbox_can_socket0'):
            self.textbox_can_socket0.delete("1.0", tk.END)
            self.textbox_can_socket0.insert("1.0", self.CAN_SOCKET0)
        if hasattr(self, 'textbox_can_socket1'):
            self.textbox_can_socket1.delete("1.0", tk.END)
            self.textbox_can_socket1.insert("1.0", self.CAN_SOCKET1)
        if hasattr(self, 'textbox_udp_port'):
            self.textbox_udp_port.delete("1.0", tk.END)
            self.textbox_udp_port.insert("1.0", self.UDP_PORT)
        if hasattr(self, 'textbox_path_dbc_can0'):
            self.textbox_path_dbc_can0.delete("1.0", tk.END)
            self.textbox_path_dbc_can0.insert("1.0", self.PATH_DBC_CAN0)
        if hasattr(self, 'textbox_path_dbc_can1'):
            self.textbox_path_dbc_can1.delete("1.0", tk.END)
            self.textbox_path_dbc_can1.insert("1.0", self.PATH_DBC_CAN1)
    
    def save_to_config_file(self):
        if self.PATH_CONFIG_MODEL != "Path":
            with open(self.PATH_CONFIG_MODEL, 'w') as f:
                f.write(f"PATH_DBC_CAN0={self.PATH_DBC_CAN0}\n")
                f.write(f"PATH_DBC_CAN1={self.PATH_DBC_CAN1}\n")
                f.write(f"UDP_PORT={self.UDP_PORT}\n")
                f.write(f"IP_SCANNER={self.IP_SCANNER}\n")
                f.write(f"CAN0_PORT={self.CAN0_PORT}\n")
                f.write(f"CAN1_PORT={self.CAN1_PORT}\n")
                f.write(f"CAN_SOCKET0={self.CAN_SOCKET0}\n")
                f.write(f"CAN_SOCKET1={self.CAN_SOCKET1}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Serial CSV to UDP JSON Translator GUI.")
    parser.add_argument('--config', type=str, help='Path to the configuration file')
    parser.add_argument('--mode', type=str, default="Cannelloni", help='Functioning mode to use: Cannelloni or PhysicalCAN')
    parser.add_argument('--nogui', action='store_true', default=False, help='Connect directly without showing the GUI')
    args = parser.parse_args()

    gui = GUI(config_path=args.config, mode=args.mode, direct_connect=args.nogui)