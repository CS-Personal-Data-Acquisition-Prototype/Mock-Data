# Mock Data Generator and Transmitter

A set of tools for generating and transmitting mock sensor data for testing and development purposes. This repository contains Python scripts that simulate sensor data acquisition and transmission to a server.

## Overview

This toolkit consists of two main components:
1. `create_data.py` - Generates mock sensor data at specified rates
2. `read_data.py` - Reads and transmits the generated data to a server

## Setup

1. Clone this repository to your local machine
2. Ensure Python 3.6+ is installed
3. Install required Python packages:
   ```
   pip install pyserial sqlite3
   ```
   
   Note: The `pyserial` package is required for USB serial communication with the Raspberry Pi.
   If you get the error "Import 'serial' could not be resolved from source", run the above command.

## Usage Instructions 

### Generate Mock Data

The `create_data.py` script creates a single SQLite database with all sensor data in one table.

```bash
python create_data.py [latitude] [longitude] [altitude]
```

- Optional parameters:
  - `latitude`: Center point for generating random GPS latitude (default: 44.56457)
  - `longitude`: Center point for generating random GPS longitude (default: -123.26204)
  - `altitude`: Center point for generating random altitude (default: 256)

This script will:
- Create a database file `data_acquisition.db`
- Generate 6000 samples (1 minute of data at 100Hz)
- Include session IDs to group related data

### Read and Transmit Data

The `read_data.py` script reads data from the SQLite database and transmits it to a server according to configuration settings.

```bash
python read_data.py
```

This script uses a configuration file (`config.ini`) to determine how to read and transmit the data.

### Configuration File Format

The `config.ini` file contains settings for the data reader and transmitter. Below is an example configuration:

```ini
[SERVER]
host = example.com
port = 8080
endpoint = /api/data
use_ssl = true
api_key = your_api_key_here

[DATABASE]
path = data_acquisition.db
query_limit = 100

[TRANSMISSION]
frequency = 10
batch_size = 50
timeout = 30
retry_attempts = 3

[LOGGING]
level = INFO
file = transmission.log
```

#### Configuration Sections

1. **SERVER**: Settings for the remote server connection
   - `host`: Server hostname or IP address
   - `port`: Server port number
   - `endpoint`: API endpoint for data submission
   - `use_ssl`: Whether to use HTTPS (true/false)
   - `api_key`: Authentication key for the API

2. **DATABASE**: Database connection settings
   - `path`: Path to the SQLite database file
   - `query_limit`: Maximum number of records to retrieve per query

3. **TRANSMISSION**: Data transmission parameters
   - `frequency`: How often to send data (in seconds)
   - `batch_size`: Number of records to send in each batch
   - `timeout`: Connection timeout in seconds
   - `retry_attempts`: Number of retry attempts if transmission fails

4. **LOGGING**: Logging configuration
   - `level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - `file`: Path to the log file

### Database Structures

#### Single Database (`data_acquisition.db`)
Contains one table `sensor_data` with the following fields:
- `id` - Auto-incrementing primary key
- `sessionID` - Identifier for grouping related data points
- `timestamp` - ISO format timestamp
- `latitude`, `longitude`, `altitude` - GPS coordinates
- `accel_x`, `accel_y`, `accel_z` - Accelerometer readings
- `gyro_x`, `gyro_y`, `gyro_z` - Gyroscope readings
- `dac_1`, `dac_2`, `dac_3`, `dac_4` - DAC channel readings

## Data Format and Ranges

- GPS coordinates:
  - Latitude: -90° to +90°
  - Longitude: -180° to +180°
  - Altitude: 0 to 1000 meters
- Accelerometer: -10 to +10 (X, Y, Z axes)
- Gyroscope: -500 to +500 (X, Y, Z axes)
- DAC Channels: 0 to 5 (4 channels)

## License Notice
To apply the Apache License to your work, attach the following boilerplate notice. The text should be enclosed in the appropriate comment syntax for the file format. We also recommend that a file or class name and description of purpose be included on the same "printed page" as the copyright notice for easier identification within third-party archives.

    Copyright 2025 CS 462 Personal Data Acquisition Prototype Group
    
    Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
    
    http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
