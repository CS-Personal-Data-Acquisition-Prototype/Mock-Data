/*
Copyright 2025 CS 46X Personal Data Acquisition Prototype Group
    
    Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. 
    You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
use chrono::Utc;
use rand::{rngs::ThreadRng, Rng};

const FORCE_SEED: u16 = 15;
const FORCE_RANGE: u16 = 10;

const LINEAR_SEED: u16 = 12;
const LINEAR_RANGE: u16 = 6;

const STRING_SEED: u16 = 10;
const STRING_RANGE: u16 = 8;

const ACCEL_SEED: f32 = 0.;
const ACCEL_RANGE: f32 = 5.;
const GYRO_SEED: f32 = 0.;
const GYRO_RANGE: f32 = 10.;
const MAG_SEED: f32 = 0.;
const MAG_RANGE: f32 = 50.;

const LAT_SEED: f32 = 44.56457;
const LON_SEED: f32 = -123.26204;
const GPS_RANGE: f32 = 1.;

pub struct DataPoint {
    timestamp: String,
    gps: (f32, f32),
    accel: (f32, f32, f32),
    gyro: (f32, f32, f32),
    mag: (f32, f32, f32),
    force: u16,
    linear: u16,
    string: u16,
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

fn gen_force(rng: &mut ThreadRng) -> u16 {
    rng.random_range((FORCE_SEED - FORCE_RANGE)..=(FORCE_SEED + FORCE_RANGE))
}

fn gen_gps(rng: &mut ThreadRng) -> (f32, f32) {
    (
        rng.random_range((LAT_SEED - GPS_RANGE)..=(LAT_SEED + GPS_RANGE)),
        rng.random_range((LON_SEED - GPS_RANGE)..=(LON_SEED + GPS_RANGE)),
    )
}

fn gen_linear(rng: &mut ThreadRng) -> u16 {
    rng.random_range((LINEAR_SEED - LINEAR_RANGE)..=(LINEAR_SEED + LINEAR_RANGE))
}

fn gen_string(rng: &mut ThreadRng) -> u16 {
    rng.random_range((STRING_SEED - STRING_RANGE)..=(STRING_SEED + STRING_RANGE))
}

fn gen_9dof(rng: &mut ThreadRng) -> (f32, f32, f32, f32, f32, f32, f32, f32, f32) {
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
