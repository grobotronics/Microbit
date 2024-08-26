from microbit import *
from time import sleep
from GRobotronicsHuskyLens import HuskyLens

machine_vision = HuskyLens()

while True:
    # Request the number of learned IDs
    learned_ids = machine_vision.count_learned_ids()
    print("Number of learned IDs:", learned_ids)

    # Request the number of frames displayed on screen
    frames =  machine_vision.count_frames()
    print("Number of frames:", frames)

    # Request the number of frames displayed on screen with a particular id
    id_number = 1
    frames_counted = machine_vision.count_frames_id(id_number)
    print("Number of frames with ID", id_number, ":", frames_counted)

    # Request all data of all frames displayed on screen
    frame = machine_vision.request_frames()
    print("Data of frame:", frame["frames"])

    # Request all data of all arrows displayed on screen
    arrow = machine_vision.request_arrows()
    print("Data of arrow:", arrow["arrows"])

    # Request all x values of all frames displayed on screen
    x_list = machine_vision.get_x_values()
    print("List of x values:", x_list)

    # Request all y values of all frames displayed on screen
    y_list = machine_vision.get_y_values()
    print("List of y values:", y_list)

    # Request all width values of all frames displayed on screen
    width_list = machine_vision.get_width_values()
    print("List of width values:", width_list)
    
    # Request all height values of all frames displayed on screen
    height_list = machine_vision.get_height_values()
    print("List of height values:", height_list)

    # Request all x1 values of all arrows displayed on screen
    x1_list = machine_vision.get_x1_values()
    print("List of x1 values:", x1_list)

    # Request all y1 values of all arrows displayed on screen
    y1_list = machine_vision.get_y1_values()
    print("List of y1 values:", y1_list)

    # Request all x2 values of all arrows displayed on screen
    x2_list = machine_vision.get_x2_values()
    print("List of x2 values:", x2_list)

    # Request all y2 values of all arrows displayed on screen
    y2_list = machine_vision.get_y2_values()
    print("List of y2 values:", y2_list)
    
    print("*******************************")
    sleep(1)
