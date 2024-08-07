from microbit import *
import radio
import ustruct
from utime import sleep_us
from machine import time_pulse_us

I2C_ADDR = 0x10
ADC_REGISTERS = [0x1E, 0x20, 0x22, 0x24, 0x26]
LEFT_LED_REGISTER = 0x0B
RIGHT_LED_REGISTER = 0x0C
LEFT_MOTOR_REGISTER = 0x00
RIGHT_MOTOR_REGISTER = 0x02
SERVO1_REGISTER = 0x14
SERVO2_REGISTER = 0x15

# Control front LEDs (Maqueen Plus V2)
class LEDController:
    def __init__(self):
        i2c.init()

    def control_led(self, led, switch):
        buf = bytearray(2)
        
        if led == "LEFT":
            buf[0] = LEFT_LED_REGISTER
        elif led == "RIGHT":
            buf[0] = RIGHT_LED_REGISTER
        buf[1] = switch
        i2c.write(I2C_ADDR, buf)

# Read values from distance sensor (Maqueen Lite / Maqueen Plus V2)
class DistanceSensor:
    def __init__(self, trigger, echo):
        self.trigger = trigger
        self.echo = echo
        self.echo.set_pull(self.echo.NO_PULL)
        self.trigger.set_pull(self.trigger.NO_PULL)

    def get_distance(self):
        self.trigger.write_digital(0)
        sleep_us(2)
        self.trigger.write_digital(1)
        sleep_us(10)
        self.trigger.write_digital(0)
        
        duration = time_pulse_us(self.echo, 1)

        distanceCM = duration * 0.034 / 2  # Distance in cm
        distanceCM = round(distanceCM)
        
        if 2 < distanceCM < 400:
            return distanceCM
        else:
            return 0  # Out of range

# Read values from line sensors - Digital read mode (Maqueen Plus V2)
class LineSensors:
    def __init__(self):
        i2c.init()

    def read_sensor_data(self, register):
        i2c.write(I2C_ADDR, bytearray([register]))
        data = i2c.read(I2C_ADDR, 2)
        return ustruct.unpack('<H', data)[0]

    def get_color(self, sensor_value):
        if sensor_value < 150:
            return "BLACK"
        else:
            return "WHITE"

    def return_sensor_values(self):
        sensor_values = [self.read_sensor_data(reg) for reg in ADC_REGISTERS]

        R2 = self.get_color(sensor_values[0])
        R1 = self.get_color(sensor_values[1])
        M = self.get_color(sensor_values[2])
        L1 = self.get_color(sensor_values[3])
        L2 = self.get_color(sensor_values[4])

        return L2, L1, M, R1, R2

# Read values from line sensors - Analog read mode (Maqueen Plus V2)
class LineSensorsADC:
    def __init__(self):
        i2c.init()

    def read_sensor_data(self, register):
        i2c.write(I2C_ADDR, bytearray([register]))
        data = i2c.read(I2C_ADDR, 2)
        return ustruct.unpack('<H', data)[0]

    def return_sensor_values(self):
        sensor_values = [self.read_sensor_data(reg) for reg in ADC_REGISTERS]

        R2 = sensor_values[0]
        R1 = sensor_values[1]
        M = sensor_values[2]
        L1 = sensor_values[3]
        L2 = sensor_values[4]

        return L2, L1, M, R1, R2

# Move robot (Maqueen Lite / Maqueen Plus V2)
class MoveMaqueen:
    def __init__(self):
        i2c.init()
    
    def move(self, LeftMotor, RightMotor):
        def set_motor_speed(motor, speed):
            buf = bytearray(3)
            # Select motor: 0 for M1(left motor), 1 for M2(right motor)
            buf[0] = LEFT_MOTOR_REGISTER if motor == 0 else RIGHT_MOTOR_REGISTER
            # Select direction: 0 for CW, 1 for CCW
            buf[1] = 0 if speed >= 0 else 1
            # Map values from [-100, 100] to [0, 255]
            buf[2] = abs(speed) * 255 // 100
            i2c.write(I2C_ADDR, buf)
        # Set speed for left and right motor
        set_motor_speed(0, LeftMotor)
        set_motor_speed(1, RightMotor)

    def stop(self):
        self.move(0, 0)

# Control servos (Maqueen Plus V2)
class PlusV2ServoController:
    def __init__(self, pin):
        self.servo_pin = pin
        self.servo_pin.set_analog_period(20)  # f=50Hz -> T=20ms

    def set_servo(self, degrees):
        if degrees < 0:
            degrees = 0
        elif degrees > 180:
            degrees = 180

        pulse_duration = (degrees / 90) + 0.5  # 0.5ms -> 0deg, 2.5ms -> 180deg
        duty = (100 * pulse_duration) / 20     # 0% -> 0ms, 100% -> 20ms
        servo_value = (1023 * duty) / 100      # 0 -> 0%, 1023 -> 100%

        self.servo_pin.write_analog(servo_value)

# Control servos (Maqueen Lite)
class LiteServoController:
    def __init__(self):
        i2c.init()

    def set_servo(self, servo, angle):
        buf = bytearray(2)
        if servo == "SERVO1":
            buf[0] = SERVO1_REGISTER
        elif servo == "SERVO2":
            buf[0] = SERVO2_REGISTER
        buf[1] = angle
        i2c.write(I2C_ADDR, buf)
 
# Read values from DFRobot GamePad V4 - Digital read mode (Maqueen Lite / Maqueen Plus V2)
class DigitalGamePad:
    def __init__(self):
        radio.on()

    def get_message(self):
        messageReceived = radio.receive()
        if messageReceived:
            if len(messageReceived) < 4:  # if length of message is less than 4 then speed value was sent
                speed = int(messageReceived)
                return speed
            else:
                return messageReceived

# Read values from DFRobot GamePad V4 - Analog read mode (Maqueen Lite / Maqueen Plus V2)
class AnalogGamePad:
    def __init__(self):
        radio.on()
        
    def map_value(self, value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def get_speeds(self):
        messageReceived = radio.receive()
        if messageReceived:
            Xvalue_str = messageReceived[:4]  # Keep first 4 digits
            Yvalue_str = messageReceived[4:]  # Keep last 4 digits
            Xvalue = int(Xvalue_str)  
            Yvalue = int(Yvalue_str)
            # Map values from (0, 1023) to (-100, 100)
            mappedX = self.map_value(Xvalue, 0, 1023, -100, 100)
            mappedY = self.map_value(Yvalue, 0, 1023, -100, 100)
            # Set speed of motors based on mappedX and mappedY values
            leftSpeed = mappedY + mappedX
            rightSpeed = mappedY - mappedX
            # Ensure speed values are in range (-100, 100)
            leftSpeed = max(min(leftSpeed, 100), -100)
            rightSpeed = max(min(rightSpeed, 100), -100)
            # Ensure robot will not flicker when joystick remains in the center position
            if leftSpeed > -10 and leftSpeed < 10:
                leftSpeed = 0
            if rightSpeed > -10 and rightSpeed < 10:
                rightSpeed = 0
            return leftSpeed, rightSpeed
        else:
            return 0, 0
