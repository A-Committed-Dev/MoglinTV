import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class Accelerometer:
    
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.ads.gain = 1  # +/-4.096 V full-scale
        self.ZERO_G_VOLTAGE = 1.65  # ADXL335 outputs ~1.65V at 0g
        self.SENSITIVITY = 0.300     # V/g (300 mV/g)
        self.x = AnalogIn(self.ads, ADS.P2)
        self.y = AnalogIn(self.ads, ADS.P1)
        self.z = AnalogIn(self.ads, ADS.P0)
        self.prev_x, self.prev_y, self.prev_z = self.read()  # For shake detection
    
    def voltage_to_g(self, v: float) -> float:
        return (v - self.ZERO_G_VOLTAGE) / self.SENSITIVITY
    
    def read(self):
        x = self.voltage_to_g(self.x.voltage)   
        y = self.voltage_to_g(self.y.voltage) 
        z = self.voltage_to_g(self.z.voltage)
        return x, y, z

    def shake(self, threshold: float = 1.0) -> bool:
        x, y, z = self.read()
        shaken = (
            abs(x - self.prev_x) > threshold
            or abs(y - self.prev_y) > threshold
            or abs(z - self.prev_z) > threshold
        )
        self.prev_x, self.prev_y, self.prev_z = x, y, z
        return shaken
            