# Modified from https://github.com/crispyDyne/mock_daq_data by Chris Patton

import sqlite3
import csv
import socket
import time
from datetime import datetime
import sys
import configparser
import os
import serial
import serial.tools.list_ports

datafile = "mockdata.csv"


# Function to load configuration from config.ini file
def load_config():
    config = configparser.ConfigParser()
    config_file = "config.ini"
    
    # Default values
    default_config = {
        'server': {
            'ip': '127.0.0.1',
            'port': '7878',
            'max_retries': '3',
            'retry_delay': '2'
        }, 
        'connection': {
            'preferred_method': 'usb',
            'auto_fallback': 'true'
        },
        'usb': {
            'baud_rate': '115200',
            'timeout': '5',
            'pi_zero_vid': '0x2e8a',
            'pi_5_vid': '0x2e8a'
        }
    }
    
    # If config file exists, read it
    if os.path.exists(config_file):
        try:
            config.read(config_file)
            print(f"Loaded configuration from {config_file}")
        except Exception as e:
            print(f"Error reading config file: {e}")
            print("Using default configuration")
            # Create config object with defaults
            for section, options in default_config.items():
                if not config.has_section(section):
                    config.add_section(section)
                for option, value in options.items():
                    config.set(section, option, value)
    else:
        # Create a new config file with defaults
        print(f"Config file not found. Creating {config_file} with default settings.")
        for section, options in default_config.items():
            config.add_section(section)
            for option, value in options.items():
                config.set(section, option, value)
        
        try:
            with open(config_file, 'w') as configfile:
                config.write(configfile)
            print(f"Created new configuration file: {config_file}")
        except Exception as e:
            print(f"Error creating config file: {e}")
            print("Using default configuration")
    
    return config


# Function to format a row with one decimal place and fixed column widths
def format_row(row, column_widths):
    formatted_values = []
    for i, value in enumerate(row):
        if value is None:
            formatted_value = "NULL" + " " * 5
        elif isinstance(value, float):
            if i == 2 or i == 3:
                formatted_value = (
                    f"{value: {column_widths[i]}.2f}"  # Fixed width with 2 decimal places
                )
            else:
                formatted_value = (
                    f"{value: {column_widths[i]}.1f}"  # Fixed width with 1 decimal place
                )
        elif isinstance(value, int):
            formatted_value = f"{value: {column_widths[i]}}"
        else:
            formatted_value = f"{value:<{column_widths[i]}}"  # Left-align text values
        formatted_values.append(formatted_value)
    return formatted_values


# Calculate column widths dynamically based on data
def calculate_column_widths(cursor, rows):
    column_names = [description[0] for description in cursor.description]
    column_widths = [len(name) for name in column_names]
    for row in rows:
        for i, value in enumerate(row):
            if isinstance(value, float):
                value_length = len(f"{value:.1f}")
            else:
                value_length = len(str(value))
            column_widths[i] = max(column_widths[i], value_length)
    return column_widths


# Function to read data from the database and print it to the console
def read_data():
    # Connect to the SQLite database
    conn = sqlite3.connect("data_acquisition.db")
    cursor = conn.cursor()

    # Query the data
    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp")
    rows = cursor.fetchall()
    
    # Check if we have enough data
    if len(rows) == 0:
        print("No data found in database. Run create_data.py first.")
        return
        
    print(f"Found {len(rows)} samples in database.")
    
    # Calculate column widths
    column_widths = calculate_column_widths(cursor, rows)

    # Print header info
    column_names = [description[0] for description in cursor.description]
    header = " | ".join(
        [f"{name:<{column_widths[i]}}" for i, name in enumerate(column_names)]
    )
    print(header)
    print("-" * len(header))
    
    # Print first few rows as examples
    sample_size = min(5, len(rows))
    for i in range(sample_size):
        formatted_row = format_row(rows[i], column_widths)
        print(" | ".join(formatted_row))
    
    if len(rows) > sample_size:
        print("... (more rows) ...")
        
    # Close the database connection
    conn.close()

    # Send data to Pi
    send_data_to_server(rows)


# Function to find the Raspberry Pi if connected via USB
def find_raspberry_pi_usb():
    """Find Raspberry Pi USB serial device."""
    print("Searching for Raspberry Pi USB connection...")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Check for Raspberry Pi VID (vendor ID)
        if "2e8a" in port.hwid.lower():  # Common Pi vendor ID
            print(f"Found Raspberry Pi on {port.device}")
            return port.device
        # Check for common names
        if "serial" in port.description.lower() and "pi" in port.description.lower():
            print(f"Found likely Raspberry Pi on {port.device}")
            return port.device
    print("No Raspberry Pi USB device found")
    return None


# Function to send data to Pi if connected via USB
def send_data_via_usb(rows, config):
    """Send data via USB serial connection."""
    baudrate = config.getint('usb', 'baud_rate')
    timeout = config.getint('usb', 'timeout')
    
    # Find the Raspberry Pi USB device
    device_path = find_raspberry_pi_usb()
    if not device_path:
        print("USB connection failed: No Raspberry Pi device found")
        return False
    
    try:
        print(f"Opening USB serial connection at {baudrate} baud")
        with serial.Serial(device_path, baudrate, timeout=timeout) as ser:
            # Calculate sample rate from data
            timestamp_index = 2
            
            try:
                # Try to parse timestamps as datetime objects
                start_time = datetime.fromisoformat(rows[0][timestamp_index])
                end_time = datetime.fromisoformat(rows[-1][timestamp_index])
                transmission_interval = (end_time - start_time).total_seconds() / len(rows)
            except (ValueError, TypeError):
                # If parsing fails, use 100Hz as default
                transmission_interval = 0.01  # 100 Hz
            
            sample_rate = 1.0 / transmission_interval
            print(f"USB Connection: Sending {len(rows)} samples at ~{sample_rate:.1f} Hz")
            
            # Track timing for consistent rate
            start_time = time.time()
            next_send_time = start_time
            
            # Send data at the specified rate
            for i, row in enumerate(rows):
                # Calculate when this packet should be sent
                next_send_time = start_time + (i * transmission_interval)
                
                # Wait if we're ahead of schedule
                current_time = time.time()
                if next_send_time > current_time:
                    time.sleep(next_send_time - current_time)
                
                # Send the data
                data = ",".join(map(str, row)) + "\n"
                ser.write(data.encode('utf-8'))
                
                # Print status occasionally
                if i % 100 == 0 or i == len(rows) - 1:
                    print(f"Sent {i+1}/{len(rows)} samples ({(i+1)/len(rows)*100:.1f}%)")
                    elapsed = time.time() - start_time
                    actual_rate = (i+1) / elapsed if elapsed > 0 else 0
                    print(f"Elapsed: {elapsed:.2f}s, Rate: {actual_rate:.1f} Hz", end="\r")
                    sys.stdout.flush()
            
            elapsed = time.time() - start_time
            print(f"\nUSB transmission complete. Sent {len(rows)} samples in {elapsed:.2f} seconds.")
            return True
            
    except Exception as e:
        print(f"USB connection failed: {e}")
        return False


# No USB to Pi or Pi connection fails
def send_data_via_wifi(rows, config):
    """Send data via WiFi TCP connection."""
    # Get server settings from config
    server_ip = config.get('server', 'ip')
    server_port = config.getint('server', 'port')
    max_retries = config.getint('server', 'max_retries')
    retry_delay = config.getint('server', 'retry_delay')
    
    print(f"Using WiFi connection to server: {server_ip}:{server_port}")
    
    # Calculate sample rate from data
    timestamp_index = 2  
    
    try:
        # Try to parse timestamps as datetime objects
        start_time = datetime.fromisoformat(rows[0][timestamp_index])
        end_time = datetime.fromisoformat(rows[-1][timestamp_index])
        transmission_interval = (end_time - start_time).total_seconds() / len(rows)
    except (ValueError, TypeError):
        # If parsing fails, use 100Hz as default
        transmission_interval = 0.01  # 100 Hz
    
    sample_rate = 1.0 / transmission_interval
    print(f"WiFi Connection: Sending {len(rows)} samples at ~{sample_rate:.1f} Hz")
    
    for attempt in range(max_retries):
        try:
            print(f"\nWiFi attempt {attempt + 1}/{max_retries}")
            
            print(f"Creating socket for {server_ip}:{server_port}")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                print(f"Attempting WiFi connection...")
                s.connect((server_ip, server_port))
                print("WiFi connected successfully!")
                
                # Track timing for consistent rate
                start_time = time.time()
                next_send_time = start_time
                
                # Send data at the specified rate
                for i, row in enumerate(rows):
                    # Calculate when this packet should be sent
                    next_send_time = start_time + (i * transmission_interval)
                    
                    # Wait if we're ahead of schedule
                    current_time = time.time()
                    if next_send_time > current_time:
                        time.sleep(next_send_time - current_time)
                    
                    # Send the data
                    data = ",".join(map(str, row)) + "\n"
                    s.sendall(data.encode('utf-8'))
                    
                    # Print status occasionally
                    if i % 100 == 0 or i == len(rows) - 1:
                        print(f"Sent {i+1}/{len(rows)} samples ({(i+1)/len(rows)*100:.1f}%)")
                        elapsed = time.time() - start_time
                        actual_rate = (i+1) / elapsed if elapsed > 0 else 0
                        print(f"Elapsed: {elapsed:.2f}s, Rate: {actual_rate:.1f} Hz", end="\r")
                        sys.stdout.flush()
                
                elapsed = time.time() - start_time
                print(f"\nWiFi transmission complete. Sent {len(rows)} samples in {elapsed:.2f} seconds.")
                return True
                
        except Exception as e:
            print(f"WiFi connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying WiFi in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print("All WiFi connection attempts failed.")
    return False


# Send data to the server on the Pi
def send_data_to_server(rows):
    """Send data to Raspberry Pi with fallback capability."""
    # Load configuration
    config = load_config()
    
    # Get preferred connection method
    preferred_method = config.get('connection', 'preferred_method', fallback='usb').lower()
    auto_fallback = config.getboolean('connection', 'auto_fallback', fallback=True)
    
    success = False
    
    # Try the preferred method first
    if preferred_method == 'usb':
        print("Trying USB connection as preferred method...")
        success = send_data_via_usb(rows, config)
        
        # Fall back to WiFi if needed and fallback is enabled
        if not success and auto_fallback:
            print("USB connection failed. Falling back to WiFi...")
            success = send_data_via_wifi(rows, config)
    else:
        # WiFi is preferred
        print("Trying WiFi connection as preferred method...")
        success = send_data_via_wifi(rows, config)
        
        # Fall back to USB if needed and fallback is enabled
        if not success and auto_fallback:
            print("WiFi connection failed. Falling back to USB...")
            success = send_data_via_usb(rows, config)
    
    if success:
        print("Data transmission successful")
    else:
        print("ERROR: All connection methods failed")


if __name__ == "__main__":
    read_data()