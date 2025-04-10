mod create_data;
use create_data::DataPoint;
use serde::Deserialize;
use std::{
    fs,
    net::TcpStream,
    thread::sleep,
    time::{Duration, Instant},
};
use tungstenite::{connect, stream::MaybeTlsStream, Message, WebSocket};

#[derive(Deserialize)]
struct Config {
    forward_addr: String,
    max_tries: usize,
    interval: u64,
}

fn main() {
    let config = match std::env::current_dir() {
        Ok(mut path) => {
            path.push("src");
            path.push("config.toml");
            match fs::read_to_string(&path) {
                Ok(s) => match toml::from_str::<Config>(&s) {
                    Ok(config_table) => config_table,
                    Err(e) => panic!("Failed to parse config to valid toml at {:?}: {e}", path),
                },
                Err(e) => panic!("Failed to open config.toml at {:?}: {e}", path),
            }
        }
        Err(e) => panic!("Failed to get current directory: {e}"),
    };
    let interval = Duration::from_millis(config.interval);
    let mut tries = config.max_tries;
    let mut rng = rand::rng();
    let mut socket: Option<WebSocket<MaybeTlsStream<TcpStream>>> = None;
    loop {
        match socket {
            // if connected with a socket
            Some(ref mut sock) => {
                // get current time
                let start = Instant::now();
                //attempt to send data
                if let Err(_) = sock.send(Message::Binary(tungstenite::Bytes::from(
                    DataPoint::new(&mut rng).to_string(),
                ))) {
                    println!("Failed to send to socket.");
                    let _ = sock.close(None);
                    socket = None;
                    continue;
                }
                //sleep for any remaining time in interval
                let elapsed = start.elapsed();
                if elapsed < interval {
                    sleep(interval - elapsed);
                }
            }
            // if disconnected
            None => {
                //attempt to connect to socket
                socket = match connect(&config.forward_addr) {
                    //reset tries and return socket
                    Ok((mut s, _)) => {
                        tries = config.max_tries;
                        if let Err(e) = s.send(Message::Binary(vec![b'S'].into())) {
                            eprintln!("Failed to send initial message: {e}");
                        }
                        Some(s)
                    }
                    // If more tries, reattempt after 1 second, else exit.
                    Err(_) => {
                        println!("Failed to connect to reciever.");
                        if tries > 0 {
                            println!("Retrying in 1 second...");
                            tries -= 1;
                            sleep(Duration::from_secs(1));
                            continue;
                        } else {
                            println!("Attempted max tries. Exiting now.");
                            return;
                        }
                    }
                };
            }
        }
    }
}
