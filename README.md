# SCanner-adapter
Cannelloni UDP to JSON stream translator

## General schema
![General schema](img/general-schema.png)

## How to use
### Install dependencies
```bash
pip install -r requirements.txt
```

### CONFIG file
To configure the parameters of the program you have to create a 'CONFIG.txt' file with the following parameters:
```txt
PATH_DBC_CAN0=Path
PATH_DBC_CAN1=Path
IP_SCANNER=8.8.8.8
CAN0_PORT=9600
CAN1_PORT=9601
UDP_PORT=5000
```
The 'PATH_DBC_CAN0' and 'PATH_DBC_CAN1' parameters are the paths to the DBC files of the CAN0 and CAN1 buses respectively. The 'IP_SCANNER' parameter is the IP address of the scanner. The 'CAN0_PORT' and 'CAN1_PORT' parameters are the ports of the CAN0 and CAN1 buses respectively. The 'UDP_PORT' parameter is the port of the local UDP server.

...

### Build executable
```bash
pyinstaller --name SCannerAdapter  main.py --onefile --windowed
```

## Tech stack
- Python 3.12.2
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [Cannelloni](https://github.com/mguentner/cannelloni)
- [Cantools](https://pypi.org/project/cantools/)
- [PlotJuggler](https://github.com/facontidavide/PlotJuggler)
