import time
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys, time, math
from playsound import playsound
import socket
import webbrowser

xsize=100
ysize=0.002
y_list=[]
# Configure the serial port
try:
    ser = serial.Serial(
        port='COM8',  # Make sure this is the correct port for your device
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1  # Add a timeout for readline() to return even if no data is received
    )
except serial.SerialException as e:
    print(f"Error opening the serial port: {e}")
    sys.exit(1)

if ser.isOpen():
    print("Serial port is open.")
else:
    print("Failed to open serial port.")
    sys.exit(1)

last_val = None  # Initialize a variable to store the last value
temp_type = 'uF'
title = 'Capacitance'
colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'black', 'pink']
color_index = 0  # Index to keep track of the current color


def serial_read(ser):
    global last_val, color_index
    t = -0.5  # Initialize time
    while True:
        t+=0.5
        try:
            strin = ser.readline()
            if strin:
                strin = strin.rstrip()
                strin = strin.decode()
                try:
                    current_val = float(strin)  # Convert the current string to float
                    print(current_val)
                    global color_index
                    if last_val is not None and (current_val >= last_val * 1.2 or current_val <= last_val * 0.8):
                        # Update the color index to change the graph color
                        color_index = (color_index + 1) % len(colors)
                        if current_val != 0.0 and current_val > 0.00094:
                            order_of_magnitude = math.floor(math.log10(abs(current_val)))
                            # Scale the value to keep the first two significant digits
                            scaled_val = current_val / 10**order_of_magnitude
                            # Round the value to two significant digits
                            rounded_scaled_val = round(scaled_val, 2 - int(math.floor(math.log10(abs(scaled_val)))) - 1)
                            adjusted_val = rounded_scaled_val * 10**order_of_magnitude
                            formatted_val = f"{adjusted_val:.3f}"
                            search_query = f'https://www.amazon.ca/s?k={formatted_val}uF+capacitor'
                            webbrowser.open(search_query)
                    last_val = current_val  # Update last_val with the current value for the next comparison
                    yield t, current_val, colors[color_index]
                except ValueError:
                    print(f"Received non-numeric data: {strin}")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        
        
def run(data):
    t,y, current_color = data
    if t>-1:
        xdata.append(t)
        ydata.append(y)
        if t>xsize: # Scroll to the left.
            ax.set_xlim(t-xsize, t)
        line.set_data(xdata, ydata)
        line.set_color(current_color)
        # Dynamically update y-axis limits based on the current value
        current_ysize = y * 2  # Assuming 'y' is current_val
        ax.set_ylim(0, max(current_ysize, ysize))  # Use 'max' to ensure the y-axis is at least 'ysize'


        ax.set_ylabel(temp_type)
        ax.set_title(title)
        fig.canvas.draw_idle()
        latest_temp_text.set_text(f'Latest Capacitance: {y:.5f} {temp_type}')
    return line,latest_temp_text

def on_close_figure(event):
    sys.exit(0)

fig = plt.figure()
fig.canvas.mpl_connect('close_event', on_close_figure)
ax = fig.add_subplot(111)
line, = ax.plot([], [], lw=2)
ax.set_ylim(0, ysize)
ax.set_xlim(0, xsize)
ax.grid()
xdata, ydata = [], []
ax.set_xlabel('Time (s)')
ax.set_ylabel(temp_type)
ax.set_title(title)
latest_temp_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, verticalalignment='top')

# Important: Although blit=True makes graphing faster, we need blit=False to prevent
# spurious lines to appear when resizing the stripchart.
ani = animation.FuncAnimation(fig, run, frames=serial_read(ser), blit=False, interval=100,repeat=False)
plt.show()
