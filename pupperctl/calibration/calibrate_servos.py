import sys
import os
dir_path  = os.path.dirname(__file__)
repo_path = os.path.abspath(os.path.join(dir_path, '../..'))
sys.path.insert(0, repo_path)

from drivers.Servos.HardwareInterface import HardwareInterface
from drivers.Servos.Config import PWMParams, ServoParams
import numpy as np
import re

ServoCalibrationFilePath = '/sys/bus/nvmem/devices/3-00501/nvmem'

def get_motor_name(i, j):
    motor_type = {0: "abduction", 1: "inner", 2: "outer"}  # Top  # Bottom
    leg_pos = {0: "front-right", 1: "front-left", 2: "back-right", 3: "back-left"}
    final_name = motor_type[i] + " " + leg_pos[j]
    return final_name


def get_motor_setpoint(i, j):
    data = np.array([[0, 0, 0, 0], [90, 90, 90, 90], [-90, -90, -90, -90]])
    return data[i, j]


def degrees_to_radians(input_array):
    """Converts degrees to radians.
    
    Parameters
    ----------
    input_array :  Numpy array or float
        Degrees
    
    Returns
    -------
    Numpy array or float
        Radians
    """
    return input_array * np.pi / 180.0


def radians_to_degrees(input_array):
    """Converts degrees to radians.

    Parameters
    ----------
    input_array :  Numpy array or float
        Radians

    Returns
    -------
    Numpy array or float
        Degrees
    """
    return input_array * 180.0 / np.pi


def step_until(hardware_interface, axis, leg, set_point):
    """Returns the angle offset needed to correct a given link by asking the user for input.

    Returns
    -------
    Float
        Angle offset needed to correct the link.
    """
    found_position = False
    set_names = ["vertical", "horizontal", "horizontal"]
    offset = 0
    while not found_position:
        move_input = str(
            input("Enter 'a' or 'b' to move the link until it is **" + set_names[axis] + "**. Enter 'd' when done. Input: "
            )
        )
        if move_input == "a":
            offset += 1.0
            hardware_interface.set_actuator_position(
                degrees_to_radians(set_point + offset),
                axis,
                leg,
            )
        elif move_input == "b":
            offset -= 1.0
            hardware_interface.set_actuator_position(
                degrees_to_radians(set_point + offset),
                axis,
                leg,
            )
        elif move_input == "d":
            found_position = True
        print("Offset: ", offset)

    return offset


def calibrate_angle_offset(hardware_interface):
    """Calibrate the angle offset for the twelve motors on the robot. Note that servo_params is modified in-place.
    Parameters
    ----------
    servo_params : ServoParams
        Servo parameters. This variable is updated in-place.
    pi_board : Pi
        RaspberryPi object.
    pwm_params : PWMParams
        PWMParams object.
    """

    # Found K value of (11.4)
    print("The scaling constant for your servo represents how much you have to increase\nthe pwm pulse width (in microseconds) to rotate the servo output 1 degree.")
    print("This value is currently set to: {:.3f}".format(degrees_to_radians(hardware_interface.servo_params.micros_per_rad)))
    print("For newer CLS6336 and CLS6327 servos the value should be 11.333.")
    ks = input("Press <Enter> to keep the current value, or enter a new value: ")
    if ks != '':
        k = float(ks)
        hardware_interface.servo_params.micros_per_rad = k * 180 / np.pi

    hardware_interface.servo_params.neutral_angle_degrees = np.zeros((3, 4))

    for leg_index in range(4):
        for axis in range(3):
            # Loop until we're satisfied with the calibration
            completed = False
            while not completed:
                motor_name = get_motor_name(axis, leg_index)
                print("\n\nCalibrating the **" + motor_name + " motor **")
                set_point = get_motor_setpoint(axis, leg_index)

                # Zero out the neutral angle
                hardware_interface.servo_params.neutral_angle_degrees[axis, leg_index] = 0

                # Move servo to set_point angle
                hardware_interface.set_actuator_position(
                    degrees_to_radians(set_point),
                    axis,
                    leg_index,
                )

                # Adjust the angle using keyboard input until it matches the reference angle
                offset = step_until(
                    hardware_interface, axis, leg_index, set_point
                )
                print("Final offset: ", offset)

                hardware_interface.servo_params.neutral_angle_degrees[axis, leg_index] = - offset
                print("Calibrated neutral angle: ", hardware_interface.servo_params.neutral_angle_degrees[axis, leg_index])

                # Send the servo command using the new beta value and check that it's ok
                hardware_interface.set_actuator_position(
                    degrees_to_radians([0, 45, -45][axis]),
                    axis,
                    leg_index,
                )
                okay = ""
                prompt = "The leg should be at exactly **" + ["horizontal", "45 degrees", "45 degrees"][axis] + "**. Are you satisfied? Enter 'yes' or 'no': "
                while okay not in ["y", "n", "yes", "no"]:
                    okay = str(
                        input(prompt)
                    )
                completed = okay == "y" or okay == "yes"


def overwrite_ServoCalibration_file(servo_params):
    buf_matrix = np.zeros((3, 4))
    for i in range(3):
        for j in range(4):
            buf_matrix[i,j]= servo_params.neutral_angle_degrees[i,j]

    # Format array object string for np.array
    p1 = re.compile("([0-9]\.) ( *)") # pattern to replace the space that follows each number with a comma
    partially_formatted_matrix = p1.sub(r"\1,\2", str(buf_matrix))
    p2 = re.compile("(\]\n)") # pattern to add a comma at the end of the first two lines
    formatted_matrix_with_required_commas = p2.sub("],\n", partially_formatted_matrix)

    with open(ServoCalibrationFilePath, "w") as nv_f:
        _tmp = str(buf_matrix)
        _tmp = _tmp.replace('.' , ',')
        _tmp = _tmp.replace('[' , '')
        _tmp = _tmp.replace(']' , '')
        print(_tmp, file = nv_f)


def main():
    """Main program
    """
    hardware_interface = HardwareInterface()

    calibrate_angle_offset(hardware_interface)

    overwrite_ServoCalibration_file(hardware_interface.servo_params)

    print("\n\n CALIBRATION COMPLETE!\n")
    print("Calibrated neutral angles:")
    print(hardware_interface.servo_params.neutral_angle_degrees)

if __name__ == "__main__":
    main()
