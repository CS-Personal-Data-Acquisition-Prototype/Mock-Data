# Modified from https://github.com/crispyDyne/mock_daq_data by Chris Patton

import sqlite3
import random
import sys
from datetime import datetime, timedelta

lat_seed = 44.56457
lon_seed = -123.26204
alt_seed = 256

# Changed this to a function as running this outside of __main__ causes issues
def parse_argv():
    global lat_seed, lon_seed, alt_seed
    if len(sys.argv) > 1:
        lat_seed = float(sys.argv[1])
    if len(sys.argv) > 2:
        lon_seed = float(sys.argv[2])
    if len(sys.argv) > 3:
        alt_seed = float(sys.argv[3])


# Function to generate random GPS coordinates
def generate_gps():
    if lat_seed is not None:
        lat = round(random.uniform(lat_seed-1, lat_seed+1), 2)
    else:
        lat = round(random.uniform(-90.0, 90.0), 2) # latitude is 90 deg. south to 90 deg. north, not 180
    if lon_seed is not None:
        lon = round(random.uniform(lon_seed-1, lon_seed+1), 2)
    else:
        lon = round(random.uniform(-180.0, 180.0), 2)
    if alt_seed is not None:
        alt = random.uniform(alt_seed-10, alt_seed+10)
    else:
        alt = random.uniform(0, 1000)  # Altitude in meters
    return lat, lon, alt


# Function to generate random accelerometer and gyroscope data
def generate_accel_gyro():
    accel = [random.uniform(-10, 10) for _ in range(3)]  # X, Y, Z acceleration
    gyro = [random.uniform(-500, 500) for _ in range(3)]  # X, Y, Z angular velocity
    return accel, gyro


# Function to generate random DAC values
def generate_dac():
    return [random.uniform(0, 5) for _ in range(4)]  # Four channels with 0-5V range


# Create database and table structure
def create_database():
    conn = sqlite3.connect("data_acquisition.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS sensor_data")
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sessionID INTEGER DEFAULT NULL,
        timestamp TEXT,
        latitude REAL,
        longitude REAL,
        altitude REAL,
        accel_x REAL,
        accel_y REAL,
        accel_z REAL,
        gyro_x REAL,
        gyro_y REAL,
        gyro_z REAL,
        dac_1 REAL,
        dac_2 REAL,
        dac_3 REAL,
        dac_4 REAL
    )
    """
    )
    conn.commit()
    conn.close()


# Insert mock data into the database
def insert_mock_data():
    conn = sqlite3.connect("data_acquisition.db")
    cursor = conn.cursor()
    
    # Define data generation parameters
    SAMPLE_RATE = 100  # samples per second
    DURATION = 60     # seconds (1 minute)
    TOTAL_SAMPLES = SAMPLE_RATE * DURATION
    
    # Generate a session ID
    session_id = int(datetime.now().timestamp())
    
    # Generate start time and calculate time increments
    start_time = datetime.now()
    
    print(f"Generating {TOTAL_SAMPLES} samples (1 minute of data at {SAMPLE_RATE}Hz)...")

    for i in range(TOTAL_SAMPLES):
        # Create timestamp with proper increments
        current_time = start_time + timedelta(seconds=i/SAMPLE_RATE)
        timestamp = current_time.isoformat()
        
        lat, lon, alt = generate_gps()
        accel, gyro = generate_accel_gyro()
        dac = generate_dac()

        cursor.execute(
            """
        INSERT INTO sensor_data (
            sessionID, timestamp, latitude, longitude, altitude,
            accel_x, accel_y, accel_z,
            gyro_x, gyro_y, gyro_z,
            dac_1, dac_2, dac_3, dac_4
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session_id,
                timestamp,
                lat,
                lon,
                alt,
                accel[0],
                accel[1],
                accel[2],
                gyro[0],
                gyro[1],
                gyro[2],
                dac[0],
                dac[1],
                dac[2],
                dac[3],
            ),
        )
        
        # Show progress
        if i % 500 == 0:
            print(f"Generated {i}/{TOTAL_SAMPLES} samples")
            conn.commit()

    conn.commit()
    conn.close()


# Main function
if __name__ == "__main__":
    parse_argv()
    create_database()
    insert_mock_data()
    print("Mock data written to 'data_acquisition.db'")