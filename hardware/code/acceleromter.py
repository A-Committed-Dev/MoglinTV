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
    
    def voltage_to_g(self, v: float) -> float:
        return (v - self.ZERO_G_VOLTAGE) / self.SENSITIVITY
    
    def read(self):
        x = self.voltage_to_g(AnalogIn(self.ads, ADS.P2).voltage)   
        y = self.voltage_to_g(AnalogIn(self.ads, ADS.P1).voltage) 
        z = self.voltage_to_g(AnalogIn(self.ads, ADS.P0).voltage)
        return x, y, z
    
    