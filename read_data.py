# Modified from https://github.com/crispyDyne/mock_daq_data by Chris Patton

import sqlite3
import csv

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

    # Write to CSV
    with open(datafile, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)
        writer.writerows(rows)

    # Close the connection
    conn.close()


if __name__ == "__main__":
    read_data()
