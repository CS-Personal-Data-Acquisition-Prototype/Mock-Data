mod create_data;
use create_data::DataPoint;
use std::{
    net::TcpStream,
    thread::sleep,
    time::{Duration, Instant},
};
use tungstenite::{connect, stream::MaybeTlsStream, Message, WebSocket};

const FORWARD_ADDR: &str = "";
const MAX_TRIES: u8 = 3;
const INTERVAL: Duration = Duration::from_millis(10); //100Hz

fn main() {
    let mut tries = MAX_TRIES;
    let mut rng = rand::rng();
    let mut socket: Option<WebSocket<MaybeTlsStream<TcpStream>>> = None;
    loop {
        match socket {
            // if connected with a socket
            Some(ref mut sock) => {
                // get current time
                let start = Instant::now();
                //attempt to send data
                if let Err(_) = sock.write(Message::Binary(tungstenite::Bytes::from(
                    DataPoint::new(&mut rng).to_bytes(),
                ))) {
                    println!("Failed to write to socket.");
                    let _ = sock.close(None);
                    socket = None;
                    continue;
                }
                //sleep for any remaining time in interval
                let elapsed = start.elapsed();
                if elapsed < INTERVAL {
                    sleep(INTERVAL - elapsed);
                }
            }
            // if disconnected
            None => {
                //attempt to connect to socket
                socket = match connect(FORWARD_ADDR) {
                    //reset tries and return socket
                    Ok((s, _)) => {
                        tries = MAX_TRIES;
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
