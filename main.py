import tkinter as tk
from tkinter import filedialog
from backend.functions import open_stream_cannelloni, open_stream_plotjuggler
import threading

class GUI:
    PATH_DBC_CAN0 = None
    PATH_DBC_CAN1 = None
    connected = False

    def __init__(self):
        # Create a new instance of Tkinter application
        self.app = tk.Tk()
        self.startup()

    # ---------- WINDOW SETTINGS ---------------------------------------
        self.app.title("SCanner Adapter")

        # Set the width and height of the window
        self.screen_width = self.app.winfo_screenwidth()
        self.screen_height = self.app.winfo_screenheight()
        self.window_width = 500
        self.window_height = 520
        self.x_coordinate = (self.screen_width - self.window_width) // 2
        self.y_coordinate = (self.screen_height - self.window_height) // 2

        # Set the geometry of the window to position it on the center of the screen
        self.app.geometry(f"{self.window_width}x{self.window_height}+{self.x_coordinate}+{self.y_coordinate}")
        self.app.iconbitmap('img/icon.ico')

    # ---------- GUI ELEMENTS --------------------------------------------
        self.label = tk.Label(self.app, text="Hello, this is the SCanner Adapter! \nYou have to enter all the required values on the form below \n and than press connect!")
        self.label.pack(pady=10)

        # IP Scanner
        self.label_ip_scanner = tk.Label(self.app, text="IP SCanner:")
        self.label_ip_scanner.pack()
        self.textbox_ip_scanner = tk.Text(self.app, height=1, width=30)
        self.textbox_ip_scanner.insert("1.0", "8.8.8.8")                # Default IP address
        self.textbox_ip_scanner.pack()

        # CAN0 Port
        self.label_can0_port = tk.Label(self.app, text="CAN0 port:")
        self.label_can0_port.pack()
        self.textbox_can0_port = tk.Text(self.app, height=1, width=30)
        self.textbox_can0_port.insert("1.0", "1000")                        # Default CAN0 port
        self.textbox_can0_port.pack()

        # CAN1 Port
        self.label_can1_port = tk.Label(self.app, text="CAN1 port:")
        self.label_can1_port.pack()
        self.textbox_can1_port = tk.Text(self.app, height=1, width=30)
        self.textbox_can1_port.insert("1.0", "2000")                        # Default CAN1 port
        self.textbox_can1_port.pack()

        # Local port JSON relay
        self.label_local_port = tk.Label(self.app, text="Local port JSON relay (PlotJuggler):")
        self.label_local_port.pack()
        self.textbox_local_port = tk.Text(self.app, height=1, width=30)
        self.textbox_local_port.insert("1.0", "9870")                       # Default local port
        self.textbox_local_port.pack()

        # Path dbc CAN0
        self.label_path_dbc_can0 = tk.Label(self.app, text="Select path to CAN0 DBC:")
        self.label_path_dbc_can0.pack()
        self.textbox_path_dbc_can0 = tk.Text(self.app, height=1, width=50)
        self.textbox_path_dbc_can0.pack()
        self.textbox_path_dbc_can0.insert("1.0", self.PATH_DBC_CAN0)
        self.browse_button_can0 = tk.Button(self.app, text="Browse", command=self.browse_file_can0)
        self.browse_button_can0.pack()

        # Path dbc CAN1
        self.label_path_dbc_can1 = tk.Label(self.app, text="Select path to CAN1 DBC:")
        self.label_path_dbc_can1.pack()
        self.textbox_path_dbc_can1 = tk.Text(self.app, height=1, width=50)
        self.textbox_path_dbc_can1.pack()
        self.textbox_path_dbc_can1.insert("1.0", self.PATH_DBC_CAN1)
        self.browse_button_can1 = tk.Button(self.app, text="Browse", command=self.browse_file_can1)
        self.browse_button_can1.pack()

        # Connect button
        self.connect_button = tk.Button(self.app, text="Connect", command=self.connect_thread, font=("Arial", 14, "bold"), width=15, height=2)
        self.connect_button.pack(pady=20)

        # Connected status
        self.label_connected = tk.Label(self.app, text="CONNECTED!", font=("Arial", 14, "bold"))
        self.label_connected.forget()

        # Start the Tkinter event loop
        self.app.mainloop()

    # ---------- FUNCTIONS ---------------------------------------------
    def browse_file_can0(self):
        self.file_path_can0 = filedialog.askopenfilename()
        self.textbox_path_dbc_can0.delete("1.0", tk.END)
        self.textbox_path_dbc_can0.insert("1.0", self.file_path_can0)

        global PATH_DBC_CAN0
        self.PATH_DBC_CAN0 = self.file_path_can0

    def browse_file_can1(self):
        self.file_path_can1 = filedialog.askopenfilename()
        self.textbox_path_dbc_can1.delete("1.0", tk.END)
        self.textbox_path_dbc_can1.insert("1.0", self.file_path_can1)

        global PATH_DBC_CAN1
        self.PATH_DBC_CAN1 = self.file_path_can1

    def connect_thread(self):
        # Start a new thread for the connect function
        threading.Thread(target=self.connect, daemon=True).start()

    def connect(self):
        # Get the content of each textbox widget
        ip_scanner = self.textbox_ip_scanner.get("1.0", "end-1c")
        can0_port = self.textbox_can0_port.get("1.0", "end-1c")
        can1_port = self.textbox_can1_port.get("1.0", "end-1c")
        local_port = self.textbox_local_port.get("1.0", "end-1c")
        path_dbc_can0 = self.textbox_path_dbc_can0.get("1.0", "end-1c")
        path_dbc_can1 = self.textbox_path_dbc_can1.get("1.0", "end-1c")
        self.save_to_env_file() # Save the paths to the ENV file for future reuse

        # TO DO: Add connect functionality
        #open_stream_cannelloni(ip_scanner, int(can0_port), int(can1_port))
        open_stream_plotjuggler(int(local_port))

        self.label_connected.pack()

    def startup(self):
        # Fetch the old DBC path config from the config file
        with open('ENV.txt', 'r') as f:
            lines = f.readlines()
            if lines:
                for line in lines:
                    if line.startswith('PATH_DBC_CAN0='):
                        self.PATH_DBC_CAN0 = line.split('=')[1].strip()
                    elif line.startswith('PATH_DBC_CAN1='):
                        self.PATH_DBC_CAN1 = line.split('=')[1].strip()
    
    def save_to_env_file(self):
        with open('ENV.txt', 'w') as f:
            if self.PATH_DBC_CAN0:
                f.write(f"PATH_DBC_CAN0={self.PATH_DBC_CAN0}\n")
            if self.PATH_DBC_CAN1:
                f.write(f"PATH_DBC_CAN1={self.PATH_DBC_CAN1}\n")

GUI()