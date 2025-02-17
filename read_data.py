# Modified from https://github.com/crispyDyne/mock_daq_data by Chris Patton

import sqlite3
import csv
import socket
import time

datafile = "mockdata.csv"


# Function to format a row with one decimal place and fixed column widths
def format_row(row, column_widths):
    formatted_values = []
    for i, value in enumerate(row):
        if value is None:
            formatted_value = "NULL" + " " * 5
        elif isinstance(value, float):
            if i == 2 or i == 3:
                formatted_value = (
                    f"{value: {column_widths[i]}.2f}"  # Fixed width with 1 decimal place
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
    cursor.execute("SELECT * FROM sensor_data")
    rows = cursor.fetchall()

    # Calculate column widths
    column_widths = calculate_column_widths(cursor, rows)

    # Print the data with column headers
    column_names = [description[0] for description in cursor.description]
    header = " | ".join(
        [f"{name:<{column_widths[i]}}" for i, name in enumerate(column_names)]
    )
    print(header)
    print("-" * len(header))

    for row in rows:
        formatted_row = format_row(row, column_widths)  # Format each row
        print(" | ".join(formatted_row))

    # Send data to Pi
    send_data_to_server(rows)


def send_data_to_server(rows):
    server_ip = "0000.0000.0000.0000"  # Modify to have the IP of the Raspberry Pi
    server_port = 7878
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1}/{max_retries}")
            
            print(f"\nCreating socket for {server_ip}:{server_port}")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                
                # Set socket options
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Don't bind to specific interface - let OS handle routing
                print(f"Attempting connection...")
                s.connect((server_ip, server_port))
                print("Connected successfully!")
                
                # Send data as CSV lines
                for row in rows:
                    data = ",".join(map(str, row)) + "\n"
                    s.sendall(data.encode('utf-8'))
                    print(f"Sent: {data.strip()}")
                print("Data sent successfully")
                return
                
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise


if __name__ == "__main__":
    read_data()
