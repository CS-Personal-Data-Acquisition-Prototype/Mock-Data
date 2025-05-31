# Mock Data
## Overview
### Purpose
A mock data generation crate built in Rust to test throughout and latency with a mock real-time sensor system. Sends data as a JSON string utilizing websockets for increased throughput.

### Features
- 

### Repository Structure
- mock_data/
    - Cargo.toml
    - src/
        - config.toml - The programs configuration file
        - create_data.rs - Holds the mock data generation logic
        - main.rs - Holds the entrypoint as well as the networking logic

## Setup
1. Open a terminal where the repository will be cloned

2. Install the Rust toolchain if not already installed
   - run the command
      ```bash
      curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
      ```
   - Hit enter again for the default installation
   - Check it was installed correctly by running the following commands
      ```bash
      rustc --version
      cargo --version
      ```

3. Clone the repository by running the following command
   ```git
   git clone https://github.com/CS-Personal-Data-Acquisition-Prototype/Mock-Data.git
   ```

4. Edit the configuration file `config.toml` in the `src` directory
   - Follow the [Configuration](#configuration) section for format guidelines

5. Run the program by following the [Usage](#usage) section

## Configuration
The configuration file doesn't have any headers.<br>
The default values look like the following:
```toml
forward_addr = "ws://XX.X.X.XX:8080" # address of Pi module websocket server
max_tries = 3                        # max number of attempts to connect to the server
interval = 10                        # 100Hz in miliseconds
```

## Usage
This crate doesn't have any special commands, simply `cargo build` and `cargo run`.

1. Open a terminal in the directory 'mock_data'.

2. To run the project use the command `cargo run`

## License Notice
To apply the Apache License to your work, attach the following boilerplate notice. The text should be enclosed in the appropriate comment syntax for the file format. We also recommend that a file or class name and description of purpose be included on the same "printed page" as the copyright notice for easier identification within third-party archives.

    Copyright 2025 CS 46X Personal Data Acquisition Prototype Group
    
    Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. 
    You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
