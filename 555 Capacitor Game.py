import sys
import serial
import random
import time

# Define available capacitors and the tolerance range
available_capacitors = [0.001, 0.01, 0.05, 0.2, 1]  # Capacitances in uF
tolerance = 0.10  # Tolerance of 10%

try:
    ser = serial.Serial(
        port='COM8',  # Adjust this to your serial port
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
except serial.SerialException as e:
    print(f"Error opening the serial port: {e}")
    sys.exit(1)

if ser.isOpen():
    print("Serial port is open.")
else:
    print("Failed to open serial port.")
    sys.exit(1)

def calculate_target_capacitance():
    """
    Generate a target capacitance that is achievable by combining available capacitors in parallel.
    This is a simplified version that just picks a random combination.
    For a real challenge, you might want to implement a more complex algorithm.
    """
    return random.choice(available_capacitors) + random.choice(available_capacitors)  # Example: Simple random selection

def check_capacitance(current_val, target_val):
    """
    Check if the current capacitance is within the tolerance range of the target capacitance.
    """
    lower_bound = target_val * (1 - tolerance)
    upper_bound = target_val * (1 + tolerance)
    return lower_bound <= current_val <= upper_bound

def serial_read(ser):
    target_capacitance = calculate_target_capacitance()
    print(f"Target capacitance: {target_capacitance}uF. Try to achieve this by combining capacitors in parallel.")
    
    while True:
        strin = ser.readline()
        if strin:
            strin = strin.rstrip()
            strin = strin.decode()
            try:
                current_val = float(strin)
                print(f"Current capacitance: {current_val}uF")
                if check_capacitance(current_val, target_capacitance):
                    print("Congratulations! You've achieved the target capacitance.")
                    break
            except ValueError as e:
                print(f"Invalid data received: {e}")

serial_read(ser)
