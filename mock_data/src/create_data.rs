use chrono::Utc;
use rand::{rngs::ThreadRng, Rng};

const FORCE_SEED: u32 = 15;
const FORCE_RANGE: u32 = 10;

const LINEAR_SEED: u32 = 12;
const LINEAR_RANGE: u32 = 6;

const STRING_SEED: u32 = 10;
const STRING_RANGE: u32 = 8;

const ACCEL_SEED: f64 = 0.;
const ACCEL_RANGE: f64 = 5.;
const GYRO_SEED: f64 = 0.;
const GYRO_RANGE: f64 = 10.;
const MAG_SEED: f64 = 0.;
const MAG_RANGE: f64 = 50.;

const LAT_SEED: f64 = 44.56457;
const LON_SEED: f64 = -123.26204;
const GPS_RANGE: f64 = 1.;

pub struct DataPoint {
    timestamp: String,
    gps: (f64, f64),
    accel: (f64, f64, f64),
    gyro: (f64, f64, f64),
    mag: (f64, f64, f64),
    force: u32,
    linear: u32,
    string: u32,
}

impl DataPoint {
    //create new DataPoint by 'sampling sensors'
    pub fn new(rng: &mut ThreadRng) -> Self {
        let dof = gen_9dof(rng);
        DataPoint {
            timestamp: get_timestamp(),
            gps: gen_gps(rng),
            accel: (dof.0, dof.1, dof.2),
            gyro: (dof.3, dof.4, dof.5),
            mag: (dof.6, dof.7, dof.8),
            force: gen_force(rng),
            linear: gen_linear(rng),
            string: gen_string(rng),
        }
    }

    pub fn to_string(&self) -> String {
        //TODO: Figure out what the ECE data format will be (JSON, CSV, all at once, separate, ect)
        format!(
            r#"{{"timestamp": "{}", "sensor_blob": {{"lat": {}, "lon": {}, "accel_x": {}, "accel_y": {}, "accel_z": {}, "gyro_x": {}, "gyro_y": {}, "gyro_z": {}, "mag_x": {}, "mag_y": {}, "mag_z": {}, "force": {}, "linear": {}, "string": {}}} }}"#,
            self.timestamp,
            self.gps.0,
            self.gps.1,
            self.accel.0,
            self.accel.1,
            self.accel.2,
            self.gyro.0,
            self.gyro.1,
            self.gyro.2,
            self.mag.0,
            self.mag.1,
            self.mag.2,
            self.force,
            self.linear,
            self.string,
        )
    }
}

fn get_timestamp() -> String {
    Utc::now().format("%Y-%m-%d %H:%M:%S%.9f").to_string()
}

fn gen_force(rng: &mut ThreadRng) -> u32 {
    rng.random_range((FORCE_SEED - FORCE_RANGE)..=(FORCE_SEED + FORCE_RANGE))
}

fn gen_gps(rng: &mut ThreadRng) -> (f64, f64) {
    (
        rng.random_range((LAT_SEED - GPS_RANGE)..=(LAT_SEED + GPS_RANGE)),
        rng.random_range((LON_SEED - GPS_RANGE)..=(LON_SEED + GPS_RANGE)),
    )
}

fn gen_linear(rng: &mut ThreadRng) -> u32 {
    rng.random_range((LINEAR_SEED - LINEAR_RANGE)..=(LINEAR_SEED + LINEAR_RANGE))
}

fn gen_string(rng: &mut ThreadRng) -> u32 {
    rng.random_range((STRING_SEED - STRING_RANGE)..=(STRING_SEED + STRING_RANGE))
}

fn gen_9dof(rng: &mut ThreadRng) -> (f64, f64, f64, f64, f64, f64, f64, f64, f64) {
    (
        rng.random_range((ACCEL_SEED - ACCEL_RANGE)..=(ACCEL_SEED + ACCEL_RANGE)),
        rng.random_range((ACCEL_SEED - ACCEL_RANGE)..=(ACCEL_SEED + ACCEL_RANGE)),
        rng.random_range((ACCEL_SEED - ACCEL_RANGE)..=(ACCEL_SEED + ACCEL_RANGE)),
        rng.random_range((GYRO_SEED - GYRO_RANGE)..=(GYRO_SEED + GYRO_RANGE)),
        rng.random_range((GYRO_SEED - GYRO_RANGE)..=(GYRO_SEED + GYRO_RANGE)),
        rng.random_range((GYRO_SEED - GYRO_RANGE)..=(GYRO_SEED + GYRO_RANGE)),
        rng.random_range((MAG_SEED - MAG_RANGE)..=(MAG_SEED + MAG_RANGE)),
        rng.random_range((MAG_SEED - MAG_RANGE)..=(MAG_SEED + MAG_RANGE)),
        rng.random_range((MAG_SEED - MAG_RANGE)..=(MAG_SEED + MAG_RANGE)),
    )
}
