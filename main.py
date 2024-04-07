import tkinter as tk
from tkinter import filedialog

class GUI:
    def __init__(self):
        # Create a new instance of Tkinter application
        self.app = tk.Tk()

    # ---------- WINDOW SETTINGS ---------------------------------------
        # Optionally, you can set properties of the application window
        self.app.title("SCanner Adapter")

        # Set the width and height of the window
        self.screen_width = self.app.winfo_screenwidth()
        self.screen_height = self.app.winfo_screenheight()
        self.window_width = 500
        self.window_height = 500
        self.x_coordinate = (self.screen_width - self.window_width) // 2
        self.y_coordinate = (self.screen_height - self.window_height) // 2

        # Set the geometry of the window to position it on the center of the screen
        self.app.geometry(f"{self.window_width}x{self.window_height}+{self.x_coordinate}+{self.y_coordinate}")
        self.app.iconbitmap('img/icon.ico')

    # ---------- GUI ELEMENTS --------------------------------------------
        # Add widgets (e.g., labels, buttons) to the application window
        self.label = tk.Label(self.app, text="Hello, this is the SCanner Adapter! \nYou have to enter all the required values on the form below \n and than press connect!")
        self.label.pack(pady=10)

        # IP SCanner
        self.label = tk.Label(self.app, text="IP SCanner:")
        self.label.pack()
        self.default_ip_scanner = "127.192.0.1"                       # TO DO: Change this to the default IP address of the scanner
        self.textbox = tk.Text(self.app, height=1, width=30)
        self.textbox.insert("1.0", self.default_ip_scanner) 
        self.textbox.pack()

        # CAN0 Port
        self.label = tk.Label(self.app, text="CAN0 port:")
        self.label.pack()
        self.default_ip_scanner = "1000"                             # TO DO: Change this to the default CAN0 port
        self.textbox = tk.Text(self.app, height=1, width=30)
        self.textbox.insert("1.0", self.default_ip_scanner) 
        self.textbox.pack()

        # CAN1 Port
        self.label = tk.Label(self.app, text="CAN1 port:")
        self.label.pack()
        self.default_ip_scanner = "2000"                             # TO DO: Change this to the default CAN1 port
        self.textbox = tk.Text(self.app, height=1, width=30)
        self.textbox.insert("1.0", self.default_ip_scanner) 
        self.textbox.pack()

        self.textbox.pack(pady=(0, 10))

        # Local port JSON relay
        self.label = tk.Label(self.app, text="Local port JSON relay:")
        self.label.pack()
        self.default_ip_scanner = "3000"                             # TO DO: Change this to the default Local port JSON relay
        self.textbox = tk.Text(self.app, height=1, width=30)
        self.textbox.insert("1.0", self.default_ip_scanner) 
        self.textbox.pack()

        self.textbox.pack(pady=(0, 10))

        # Path dbc CAN0
        self.label = tk.Label(self.app, text="Select path to CAN0 DBC:")
        self.label.pack()
        self.textbox = tk.Text(self.app, height=1, width=50)
        self.textbox.pack()
        self.browse_button = tk.Button(self.app, text="Browse", command=self.browse_file)
        self.browse_button.pack()

        # Path dbc CAN1
        self.label = tk.Label(self.app, text="Select path to CAN1 DBC:")
        self.label.pack()
        self.textbox = tk.Text(self.app, height=1, width=50)
        self.textbox.pack()
        self.browse_button = tk.Button(self.app, text="Browse", command=self.browse_file)
        self.browse_button.pack()


        # Connect button
        self.button = tk.Button(self.app, text="Connect", command=self.connect, font=("Arial", 14, "bold"), width=15, height=2)
        self.button.pack(pady=30)

        # Start the Tkinter event loop
        self.app.mainloop()

    # ---------- FUNCTIONS ---------------------------------------------
    def browse_file(self):
        self.file_path = filedialog.askopenfilename()
        self.textbox.delete("1.0", self.tk.END)
        self.textbox.insert("1.0", self.file_path) 

    def connect(self):
        # TO DO: Add your connect functionality here
        pass

GUI()