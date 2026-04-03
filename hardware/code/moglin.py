from accelerometer import Accelerometer
from servo import Servo

class Moglin:
    def __init__(self):
        self.servo = Servo()
        self.servo.start()
        self.servo.set_servo_angle(0) # Start at center position
    
    # wiggle tail to show happiness     
    def happy(self):  
        self.servo.move_to_angle(45, duration_s=2)
        self.servo.move_to_angle(0, duration_s=2)
        self.servo.move_to_angle(-45, duration_s=2)
        self.servo.move_to_angle(0, duration_s=2)  

    # lower tail to show sadness
    def sad(self):
        self.servo.move_to_angle(-90, duration_s=2)
    
    # return tail to neutral position
    def neutral(self):
        self.servo.set_servo_angle(0)
        
    def shaken(self, threshold: float = 1.0) -> bool:
        accelerometer = Accelerometer()
        return accelerometer.shake(threshold)
    
    def upside_down(self, threshold: float = 1.0) -> bool:
        accelerometer = Accelerometer()
        x, y, z = accelerometer.read()
        return z < -threshold  # Detect if Z-axis is inverted beyond threshold (upside down)