from microbit import *
from time import sleep
import music
import neopixel
from GRobotronicsMaqueen import LEDController, LineSensors, LineSensorsADC, DistanceSensor, MoveMaqueen, PlusV2ServoController

led = LEDController()
rgb = neopixel.NeoPixel(pin15, 4)      # 4 RBG LEDs
line = LineSensors()
lineADC = LineSensorsADC()
sensor = DistanceSensor(pin13, pin14)  # (trigger pin, echo pin)
robot = MoveMaqueen()
servo1 = PlusV2ServoController(pin1) 
servo2 = PlusV2ServoController(pin2)

while True:
    # Activate buzzer for 1 second
    music.pitch(440)  # 440Hz frequency
    sleep(1)
    music.stop()
    
    # Flash front LEDs
    led.control_led("LEFT", 1)   # Turn on left LED
    led.control_led("RIGHT", 1)  # Turn on right LED
    sleep(1)
    led.control_led("LEFT", 0)   # Turn off left LED
    led.control_led("RIGHT", 0)  # Turn off right LED
    
    # Flash RGB LEDs
    rgb[0] = (255, 0, 0)    # 1st RGB LED is red
    rgb[1] = (0, 255, 0)    # 2nd RGB LED is green
    rgb[2] = (0, 0, 255)    # 3rd RGB LED is blue
    rgb[3] = (255, 255, 0)  # 4th RGB LED is yellow
    rgb.show()   # Turn on RGB LEDs
    sleep(2)
    rgb.clear()  # Turn off RGB LEDs
    
    # Print values from line sensors (digital read mode)
    for i in range(5):
        L2, L1, M, R1, R2 = line.return_sensor_values()
        print("L2:", L2, "L1:", L1, "M:", M, "R1:", R1, "R1:", R2)
        sleep(1)

    # Print values from line sensors (analog read mode)
    for i in range(5):
        L2, L1, M, R1, R2 = lineADC.return_sensor_values()
        print("L2:", L2, "L1:", L1, "M:", M, "R1:", R1, "R1:", R2)
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
    servo1.set_servo(0)    # servo 1 goes to 0 degrees
    servo2.set_servo(0)    # servo 2 goes to 0 degrees
    sleep(1)
    servo1.set_servo(90)   # servo 1 goes to 90 degrees
    servo2.set_servo(90)   # servo 2 goes to 90 degrees
    sleep(1)
    servo1.set_servo(180)  # servo 1 goes to 180 degrees
    servo2.set_servo(180)  # servo 2 goes to 180 degrees
    sleep(1)
    