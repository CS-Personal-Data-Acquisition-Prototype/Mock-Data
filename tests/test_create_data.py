import sys
import unittest
sys.path.append("..")
import create_data

class TestDataCreation(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
       create_data.lat_seed, create_data.lon_seed, create_data.alt_seed = None, None, None
    def test_generate_gps_0_seed(self):
        (lat, lon, alt) = create_data.generate_gps()
        self.assertGreaterEqual(lat, -90.0)
        self.assertLessEqual(lat, 90.0)
        self.assertGreaterEqual(lon, -180.0)
        self.assertLessEqual(lon, 180.0)
        self.assertGreaterEqual(alt, 0.0)
        self.assertLessEqual(alt, 1000.0)
    def test_generate_gps_1_seed(self):
        create_data.lat_seed = 35.7
        (lat, lon, alt) = create_data.generate_gps()
        self.assertGreaterEqual(lat, 34.7)
        self.assertLessEqual(lat, 36.7)
        self.assertGreaterEqual(lon, -180.0)
        self.assertLessEqual(lon, 180.0)
        self.assertGreaterEqual(alt, 0.0)
        self.assertLessEqual(alt, 1000.0)
    def test_generate_gps_2_seed(self):
        create_data.lat_seed = 35.7
        create_data.lon_seed = 139.7
        (lat, lon, alt) = create_data.generate_gps()
        self.assertGreaterEqual(lat, 34.7)
        self.assertLessEqual(lat, 36.7)
        self.assertGreaterEqual(lon, 138.7)
        self.assertLessEqual(lon, 140.7)
        self.assertGreaterEqual(alt, 0.0)
        self.assertLessEqual(alt, 1000.0)
    def test_generate_gps_3_seed(self):
        create_data.lat_seed = 35.7
        create_data.lon_seed = 139.7
        create_data.alt_seed = 20.0
        (lat, lon, alt) = create_data.generate_gps()
        self.assertGreaterEqual(lat, 34.7)
        self.assertLessEqual(lat, 36.7)
        self.assertGreaterEqual(lon, 138.7)
        self.assertLessEqual(lon, 140.7)
        self.assertGreaterEqual(alt, 10.0)
        self.assertLessEqual(alt, 30.0)  
    def test_generate_accel_gyro(self):
        ((ax, ay, az), (gx, gy, gz)) = create_data.generate_accel_gyro()
        self.assertGreaterEqual(ax, -10.0)
        self.assertLessEqual(ax, 10.0)
        self.assertGreaterEqual(ay, -10.0)
        self.assertLessEqual(ay, 10.0)
        self.assertGreaterEqual(az, -10.0)
        self.assertLessEqual(az, 10.0)
        self.assertGreaterEqual(ax, -500.0)
        self.assertLessEqual(gx, 500.0)
        self.assertGreaterEqual(ay, -500.0)
        self.assertLessEqual(gy, 500.0)
        self.assertGreaterEqual(az, -500.0)
        self.assertLessEqual(gz, 500.0)
    def test_generate_dac(self):
        (a0, a1, a2, a3) = create_data.generate_dac()
        self.assertGreaterEqual(a0, 0.0)
        self.assertLessEqual(a0, 5.0)
        self.assertGreaterEqual(a1, 0.0)
        self.assertLessEqual(a1, 5.0)
        self.assertGreaterEqual(a2, 0.0)
        self.assertLessEqual(a2, 5.0)
        self.assertGreaterEqual(a3, 0.0)
        self.assertLessEqual(a3, 5.0)

if __name__ == "__main__":
    unittest.main()