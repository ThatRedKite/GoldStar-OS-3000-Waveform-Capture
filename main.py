import matplotlib.colors
import serial
import matplotlib.pyplot as plt
import numpy as np
import sys
from time import sleep

START_ADDRESS = "0000"
READ_SIZE = "1000"
READ_MODE = "B"

BINARY_MODE = "B"
ASCII_MODE = "A"

DISPLAY_1 = 1
DISPLAY_2 = 2
SAVE_1 = 3
SAVE_2 = 4

S1 = "S1\r".encode("ASCII")

def gen_r_command(channel: int, start: int, size: int, mode: str) -> bytes:
    return f"R{channel}({start:04},{size:04},{mode})\r".encode("ASCII")


def gen_ro_command(channel) -> bytes:
    return f"Ro({channel})\r".encode("ASCII")

try:
    port_name = sys.argv[1]
except IndexError:
    port_name = "/dev/ttyUSB0"

try:
    baud_rate: int = int(sys.argv[2])
except IndexError:
    baud_rate = 4800

print(f"Trying port: \033[92m'{port_name}'\033[00m")

def draw_trace(ax1, x, y):
    ax1: plt.Axes
    #ax2: plt.Axes
    ax1.set_title("  ".join(display_settings), color=matplotlib.colors.XKCD_COLORS["xkcd:green"], fontsize=16)
    ax1.set_yticks([0, 32, 64, 96, 128, 162, 192, 224, 256], minor=True)
    ax1.set_xticks([0, 125, 250, 375, 500, 625, 750, 875, 1000], minor=True)
    ax1.yaxis.grid(True, which="minor")
    ax1.xaxis.grid(True, which="minor")

    ax1.set_facecolor(color=matplotlib.colors.XKCD_COLORS["xkcd:black"])

    # set the spine colors
    ax1.spines["bottom"].set_color(matplotlib.colors.XKCD_COLORS["xkcd:white"])
    ax1.spines["top"].set_color(matplotlib.colors.XKCD_COLORS["xkcd:white"])
    ax1.spines["left"].set_color(matplotlib.colors.XKCD_COLORS["xkcd:white"])
    ax1.spines["right"].set_color(matplotlib.colors.XKCD_COLORS["xkcd:white"])

    # set the axis label colors to green
    ax1.xaxis.label.set_color(matplotlib.colors.XKCD_COLORS["xkcd:green"])
    ax1.yaxis.label.set_color(matplotlib.colors.XKCD_COLORS["xkcd:green"])
    ax1.set_xlim(0, 999)
    ax1.set_ylim(0, 255)
    ax1.plot(x, y, "g")

try:
    ser = serial.Serial(
        port=port_name,
        baudrate=baud_rate,
        timeout=5,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_TWO,
        parity=serial.PARITY_NONE,
        dsrdtr=True,
        xonxoff=True
    )
    # test the communication with the oscilloscope
    channel = DISPLAY_1
    ser.write(S1)
    if not (ser.read(2) == b"A\r"):
        print("The Oscilloscope did respond but did not accept the command. Please check your wiring")

    sleep(1)  # sleep a second to give the scope some time
    ser.write(gen_ro_command(channel)) # write the "Ro" command to get the current settings
    # now that we have sent the command we need to read from the serial port until we reach the delimiter "\r"
    # since the reply is always ASCII characters, we can just convert it right away
    display_settings = ser.read_until(b"\r").decode("ASCII")
    # now we need to check if we actually got the display data or if the scope errored out (response code = "a")
    if display_settings == "a\r":
        print("Could not receive settings from the Oscilloscope.")

    # let's make the display settings actually usable by replacing the spaces
    # and split the response using "," as a seperator to make it easier to use the data
    display_settings = display_settings.replace(" ", "")
    display_settings = display_settings.replace("\r", "")
    display_settings = display_settings.split(",")

    # flush the buffers for good measure
    ser.flushInput()
    ser.flushOutput()
    sleep(0.2)  # sleep a little to give the scope some time

    #b = np.fft.fft(data*4, axis=0)
    #c = np.fft.fftfreq(n=b.size, d=1/10E3)
    fig, (ax1, ax2) = plt.subplots(2)
    fig: plt.Figure

    fig.set_facecolor(color=matplotlib.colors.XKCD_COLORS["xkcd:black"])
    #ax2.plot(c, b.real, "b")
    #ax2.set_xlim(0, 100)
    # now it's time to read the actual trace data from the scope
    # let's start by generating and sending the "Ri" command
    ser.write(gen_r_command(channel, 0, 1000, BINARY_MODE))
    # now we read until we have reached the delimiter = "\r",
    # then we convert the whole thing into a bytearray, so we can work with it more easily
    a = ser.read_until(b"\r")
    a = bytearray(a)
    plt.pause(0.3)
    # slice the list into the header and the data part
    # and use map() to convert the trace data into int and create a numpy array from it
    header = a[0:16]  # this is where we store the "header" data
    data = np.fromiter(map(lambda x: int(x), a[15::]), dtype=np.int32)  # this is where we store the trace data
    x_axis = np.linspace(0, 1000, num=1000)
    draw_trace(ax1, x_axis, data)

    plt.show()


except serial.SerialException:
    print("\033[91mCould not open the serial port!\033[00m")
    exit(255)


