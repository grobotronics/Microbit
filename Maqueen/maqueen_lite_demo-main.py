from microbit import *
from time import sleep
import music
import neopixel
from GRobotronicsMaqueen import DistanceSensor, MoveMaqueen, LiteServoController

sensor = DistanceSensor(pin1, pin2)  # (trigger pin, echo pin)
rgb = neopixel.NeoPixel(pin15, 4)    # 4 RBG LEDs
robot = MoveMaqueen()
servo = LiteServoController()

while True:
    # Activate buzzer for 1 second
    music.pitch(440)  # 440Hz frequency
    sleep(1)
    music.stop()
    
    # Flash front LEDs
    pin8.write_digital(1)   # Turn on left LED
    pin12.write_digital(1)  # Turn on right LED
    sleep(1)
    pin8.write_digital(0)   # Turn off left LED
    pin12.write_digital(0)  # Turn off right LED
    
    # Flash RGB LEDs
    rgb[0] = (255, 0, 0)    # 1st RGB LED is red
    rgb[1] = (0, 255, 0)    # 2nd RGB LED is green
    rgb[2] = (0, 0, 255)    # 3rd RGB LED is blue
    rgb[3] = (255, 255, 0)  # 4th RGB LED is yellow
    rgb.show()   # Turn on RGB LEDs
    sleep(2)
    rgb.clear()  # Turn off RGB LEDs
    
    # Print values from line sensors
    for i in range(5):
        L = pin13.read_digital()
        R = pin14.read_digital()
        print("Line-L:", L, "Line-R:", R)
        sleep(1)
        
    # Print values from distance sensor
    for i in range(5):
        distance = sensor.get_distance()
        print("distance in cm:", distance)
        sleep(1)

    # Move forward at full speed
    robot.move(100, 100)    # (left motor, right motor)
    sleep(0.5)
    robot.stop()
    
    # Move backward at full speed
    robot.move(-100, -100)  # (left motor, right motor)
    sleep(0.5)
    robot.stop()

    # Control 2 servos
    servo.control_led("SERVO1", 0)    # servo 1 goes to 0 degrees
    servo.control_led("SERVO2", 0)    # servo 2 goes to 0 degrees
    sleep(1)
    servo.control_led("SERVO1", 90)   # servo 1 goes to 90 degrees
    servo.control_led("SERVO2", 90)   # servo 2 goes to 90 degrees
    sleep(1)
    servo.control_led("SERVO1", 180)  # servo 1 goes to 180 degrees
    servo.control_led("SERVO2", 180)  # servo 2 goes to 180 degrees
    sleep(1)
    