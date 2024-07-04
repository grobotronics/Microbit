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

# MoveMaqueen class
class MoveMaqueen:
    def __init__(self):
        i2c.init(freq=100000, sda=pin20, scl=pin19)
    
    def move(self, LeftMotor, RightMotor):
        def set_motor_speed(motor, speed):
            direction = 0 if speed >= 0 else 1
            buf = bytearray(3)
            buf[0] = 0x00 if motor == 0 else 0x02   # Έλεγχος κινητήρα: 0 για M1(Left), 1 για M2(Right)
            buf[1] = 0 if direction == 0 else 1     # Έλεγχος φοράς πειστροφής: 0 για CW, 1 για CCW
            buf[2] = abs(speed) * 255 // 100        # Αντιστοιχίζει τιμές από (0, 255) σε (-100, 100)
            i2c.write(I2C_ADDR, buf)
        
        set_motor_speed(0, LeftMotor)   # Ορίζει την ταχύτητα του αριστερού κινητήρα
        set_motor_speed(1, RightMotor)  # Ορίζει την ταχύτητα του δεξιού κινητήρα

    def stop(self):
        self.move(0, 0)

# LEDController class
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

# DistanceSensor class
class DistanceSensor:
    def __init__(self, trigger, echo):
        self.trigger = trigger
        self.echo = echo
        self.echo.set_pull(self.echo.NO_PULL)
        self.trigger.set_pull(self.trigger.NO_PULL)

    def getDistance(self):
        self.trigger.write_digital(0)
        sleep_us(2)
        self.trigger.write_digital(1)
        sleep_us(10)
        self.trigger.write_digital(0)
        
        duration = time_pulse_us(self.echo, 1)

        distanceCM = duration * 0.034 / 2
        distanceCM = round(distanceCM)
        
        if 2 < distanceCM < 400:
            return distanceCM
        else:
            return 0

# LineSensors class
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

# LineSensorsForPID class
class LineSensorsForPID:
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

# DigitalGamePad class
class DigitalGamePad:
    def __init__(self):
        radio.on()

    def get_message(self):
        messageReceived = radio.receive()
        if messageReceived:
            print(messageReceived)
            if len(messageReceived) < 4:  # Αν το μήνυμα έχει μήκος < 4 τότε στάλθηκε τιμή για ταχύτητα
                speed = int(messageReceived)
                return speed
            else:
                return messageReceived

# AnalogGamePad class
class AnalogGamePad:
    def __init__(self):
        radio.on()
        
    def map_value(self, value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def get_speeds(self):
        messageReceived = radio.receive()
        if messageReceived:
            Xvalue_str = messageReceived[:4]  # Κρατάει τα 4 πρώτα ψηφία
            Yvalue_str = messageReceived[4:]  # Κρατάει τα 4 τελευταία ψηφία
            # Μετατροπή str σε int
            Xvalue = int(Xvalue_str)  
            Yvalue = int(Yvalue_str)
            # Αντιστοιχίζει τιμές από (0, 1023) σε (-100, 100)
            mappedX = self.map_value(Xvalue, 0, 1023, -100, 100)
            mappedY = self.map_value(Yvalue, 0, 1023, -100, 100)
            # Καθορίζει τις ταχύτητες των 2 κινητήρων με βάση τις τιμές των mappedX και mappedY
            leftSpeed = mappedY + mappedX
            rightSpeed = mappedY - mappedX
            # Εξασφαλίζει ότι οι τιμές των ταχυτήτων είναι εντός του εύρους (-100, 100)
            leftSpeed = max(min(leftSpeed, 100), -100)
            rightSpeed = max(min(rightSpeed, 100), -100)
            # Εξασφαλίζει ότι το ρομπότ δεν θα τρεμοπαίζει όταν το joystick είναι στην αρχική του θέση
            if leftSpeed > -10 and leftSpeed < 10:
                leftSpeed = 0
            if rightSpeed > -10 and rightSpeed < 10:
                rightSpeed = 0
            return leftSpeed, rightSpeed
        else:
            return 0, 0

# ServoController class
class ServoController:
    def __init__(self, pin):
        self.servo_pin = pin
        self.servo_pin.set_analog_period(20)  # f=50Hz -> T=20ms

    def set_servo(self, degrees):
        if degrees < 0:
            degrees = 0
        elif degrees > 180:
            degrees = 180

        pulse_duration = (degrees / 90) + 0.5  # 0.5ms -> 0deg, 2.5ms -> 180deg
        duty = (100 * pulse_duration) / 20     # 0ms -> 0%, 20ms -> 100%
        servo_value = (1023 * duty) / 100      # 0 -> 0%, 1023 -> 100%

        self.servo_pin.write_analog(servo_value)

  
