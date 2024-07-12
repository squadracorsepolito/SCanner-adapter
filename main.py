import tkinter as tk
from tkinter import filedialog, StringVar, OptionMenu
from backend.functions import start_connection_controller, disconnect
import threading
import time

class GUI:
    def __init__(self):
        # Create a new instance of Tkinter application
        self.app = tk.Tk()

        # Config parameters with default values
        self.PATH_DBC_CAN0 = "Path"
        self.PATH_DBC_CAN1 = "Path"
        self.PATH_CONFIG_MODEL = "Path"
        self.IP_SCANNER = "0.0.0.0"
        self.CAN0_PORT = 4000
        self.CAN1_PORT = 5000
        self.UDP_PORT = 9870
        self.MODE = "Cannelloni"

        global controller_thread
        controller_thread = None

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
        self.label_mode = tk.Label(self.frame, text="Select functioning mode to use:")
        self.label_mode.grid(row=1, column=1, columnspan=10)
        options = ["Cannelloni", "Physical CAN (Linux-only)"]
        self.selected_option = StringVar()
        self.selected_option.set(options[0])
        self.dropdown = OptionMenu(self.frame, self.selected_option, *options)
        self.dropdown.grid(row=2, column=1, columnspan=10, pady=10)

        # Path to CONFIG
        self.label_path_config_model = tk.Label(self.frame, text="Select path to CONFIG model to use:")
        self.label_path_config_model.grid(row=3, column=1, columnspan=10)
        self.textbox_path_config_model = tk.Text(self.frame, height=1, width=50)
        self.textbox_path_config_model.grid(row=4, column=1, columnspan=10)
        self.textbox_path_config_model.insert("1.0", self.PATH_CONFIG_MODEL)
        self.browse_button_config_model = tk.Button(self.frame, text="Browse", command=self.browse_file_config_model)
        self.browse_button_config_model.grid(row=5, column=1, columnspan=10, pady=10)

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

    def connect_thread(self):
        global controller_thread
        # Start a new thread for the connect function
        controller_thread = threading.Thread(target=self.connect, daemon=True)
        controller_thread.start()

    def connect(self):
        # Get the content of each textbox widget
        self.IP_SCANNER = self.textbox_ip_scanner.get("1.0", "end-1c")
        self.CAN0_PORT = self.textbox_can0_port.get("1.0", "end-1c")
        self.CAN1_PORT = self.textbox_can1_port.get("1.0", "end-1c")
        self.UDP_PORT = self.textbox_udp_port.get("1.0", "end-1c")
        self.PATH_DBC_CAN0 = self.textbox_path_dbc_can0.get("1.0", "end-1c")
        self.PATH_DBC_CAN1 = self.textbox_path_dbc_can1.get("1.0", "end-1c")
        self.MODE = self.selected_option.get()
        self.save_to_config_file() # Save the paths to the CONFIG file for future reuse

        print("Mode: ", self.MODE)
        start_connection_controller(self.IP_SCANNER, self.CAN0_PORT, self.CAN1_PORT, self.UDP_PORT, 
                                    self.PATH_DBC_CAN0, self.PATH_DBC_CAN1, self.label_connected, 
                                    self.connect_button, self.disconnect_button, self.MODE)

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
                elif key == "IP_SCANNER":
                    self.IP_SCANNER = value
                elif key == "CAN0_PORT":
                    self.CAN0_PORT = value
                elif key == "CAN1_PORT":
                    self.CAN1_PORT = value
                elif key == "UDP_PORT":
                    self.UDP_PORT = value

        # Update the interface with new values
        self.update_interface()

    def update_interface(self):
        self.textbox_ip_scanner.delete("1.0", tk.END)
        self.textbox_ip_scanner.insert("1.0", self.IP_SCANNER)
        self.textbox_can0_port.delete("1.0", tk.END)
        self.textbox_can0_port.insert("1.0", self.CAN0_PORT)
        self.textbox_can1_port.delete("1.0", tk.END)
        self.textbox_can1_port.insert("1.0", self.CAN1_PORT)
        self.textbox_udp_port.delete("1.0", tk.END)
        self.textbox_udp_port.insert("1.0", self.UDP_PORT)
        self.textbox_path_dbc_can0.delete("1.0", tk.END)
        self.textbox_path_dbc_can0.insert("1.0", self.PATH_DBC_CAN0)
        self.textbox_path_dbc_can1.delete("1.0", tk.END)
        self.textbox_path_dbc_can1.insert("1.0", self.PATH_DBC_CAN1)
    
    def save_to_config_file(self):
        if self.PATH_CONFIG_MODEL != "Path":
            with open(self.PATH_CONFIG_MODEL, 'w') as f:
                f.write(f"PATH_DBC_CAN0={self.PATH_DBC_CAN0}\n")
                f.write(f"PATH_DBC_CAN1={self.PATH_DBC_CAN1}\n")
                f.write(f"IP_SCANNER={self.IP_SCANNER}\n")
                f.write(f"CAN0_PORT={self.CAN0_PORT}\n")
                f.write(f"CAN1_PORT={self.CAN1_PORT}\n")
                f.write(f"UDP_PORT={self.UDP_PORT}")

GUI()