from rpi_hardware_pwm import HardwarePWM
import time

# ── SG90 Servo (hardware PWM) ────────────────────────────────────────────────
# SG90 datasheet specs:
#   Pulse width:  500–2400 µs
#   Pulse cycle:  20 ms (50 Hz)
#   Center (0°):  1500 µs
#   Range:        180° (-90° to +90°)
#   Dead band:    10 µs
#   Speed:        0.10 s/60° at 4.8V
#   Stall torque: 1.8 kgf·cm at 4.8V
#   Voltage:      4.8–6.0V
#
# RPi 5: channel 2 = GPIO 18, chip 0
# ─────────────────────────────────────────────────────────────────────────────

class Servo:
    def __init__(self, hz: int = 50, min_pulse_us: int = 500, max_pulse_us: int = 2400, pwm_channel: int = 2, pwm_chip: int = 0):
        self.SERVO_HZ = hz
        self.MIN_PULSE_US = min_pulse_us      # -90°
        self.MAX_PULSE_US = max_pulse_us     # +90°
        self.PERIOD_US = 1_000_000 / self.SERVO_HZ  # 20000 µs
        self.pwm = HardwarePWM(pwm_channel=pwm_channel, hz=self.SERVO_HZ, chip=pwm_chip)
        
    
    def set_servo_angle(self, degrees: float) -> None:
        """Set SG90 to angle in range -90..+90."""
        degrees = max(-90, min(90, degrees))
        pulse_us = self.MIN_PULSE_US + (degrees + 90) / 180 * (self.MAX_PULSE_US - self.MIN_PULSE_US)
        duty_pct = pulse_us / self.PERIOD_US * 100
        self.pwm.change_duty_cycle(duty_pct)
    
    def move_to_angle(self, degrees: float, duration_s: float) -> None:
        """Move to target angle over specified duration."""
        steps = int(duration_s * self.SERVO_HZ)
        current_duty = self.pwm.duty_cycle
        target_pulse_us = self.MIN_PULSE_US + (degrees + 90) / 180 * (self.MAX_PULSE_US - self.MIN_PULSE_US)
        target_duty = target_pulse_us / self.PERIOD_US * 100
        for step in range(1, steps + 1):
            intermediate_duty = current_duty + (target_duty - current_duty) * step / steps
            self.pwm.change_duty_cycle(intermediate_duty)
            time.sleep(1 / self.SERVO_HZ)
    
    def start(self) -> None:
        self.pwm.start(0)
    
    def stop(self) -> None:
        self.pwm.stop()