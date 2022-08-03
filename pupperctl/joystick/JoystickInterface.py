import sys
sys.path.insert(0, "../..")
import numpy as np

from modules.controller import State
from modules.controller import Command
from modules.controller import Utilities

from modules.PS4Joystick import Joystick

class JoystickInterface:
    def __init__(self, config):
        self.config = config
        self.previous_gait_toggle = 0
        self.previous_state = State.BehaviorState.REST
        self.previous_hop_toggle = 0
        self.previous_activate_toggle = 0
        self.previous_dance_activate_toggle = 0

        self.previous_dance_switch_toggle = 0
        self.previous_gait_switch_toggle = 0

        self.message_rate = 50 

        self.joystick = Joystick()
        self.joystick_error = 0
        self.joystick_invalues = None

        self.joystick_cmd = Command.Command()

    def reset_joystick_input(self):
            self.joystick_invalues = {
                'ly': -0.0, 
                'lx': 0.0, 
                'rx': 0.0, 
                'ry': -0.0, 
                'L2': -1.0, 
                'R2': -1.0, 
                'R1': False, 
                'L1': False, 
                'dpady': 0, 
                'dpadx': 0, 
                'x': False, 
                'square': False, 
                'circle': False, 
                'triangle': False, 
                'message_rate': 50}

    def get_joystick_rawinput(self):

        if self.joystick_error > 4:
            print("Joystic Connection Error")
            del self.joystick
            self.joystick = Joystick()
            self.reset_joystick_input()
            self.joystick_error = 0
            return

        try:
            values = self.joystick.get_input()
        except:
            # does not seem to be triggered
            print("Joystic Input Error")
            self.reset_joystick_input()
            return
        else:
            if values is None:
                self.joystick_error += 1
                self.reset_joystick_input()
                print("Joystic Signal Warning")
                return

        self.joystick_error = 0

        dpadx = values["dpad_right"] - values["dpad_left"]
        dpady = values["dpad_up"] - values["dpad_down"]

        self.input_joystick = {
            "rx": values["right_analog_x"], # -1 - 1
            "ry": -values["right_analog_y"], # -1 - 1
            "ly": -values["left_analog_y"], # -1 - 1
            "lx": values["left_analog_x"], # -1 - 1
            "L1": values["button_l1"],
            "L2": values["l2_analog"],
            "R1": values["button_r1"],
            "R2": values["r2_analog"],
            "x": values["button_cross"],
            "square": values["button_square"],
            "circle": values["button_circle"],
            "triangle": values["button_triangle"],
            "dpady": dpady, # -1 or 1
            "dpadx": dpadx, # -1 or 1 
            "message_rate": self.message_rate,
        }

    def get_command(self, state, do_print=False):

        self.get_joystick_rawinput()

        # command = Command.Command() # why this should be initilized every time

        ####### Handle discrete commands ########
        # Check if requesting a state transition to trotting, or from trotting to resting
        gait_toggle = self.input_joystick["R1"]
        self.joystick_cmd.trot_event = (gait_toggle == 1 and self.previous_gait_toggle == 0)

        # Check if requesting a state transition to hopping, from trotting or resting
        hop_toggle = self.input_joystick["x"]
        self.joystick_cmd.hop_event = (hop_toggle == 1 and self.previous_hop_toggle == 0)

        dance_activate_toggle = self.input_joystick["circle"]
        self.joystick_cmd.dance_activate_event = (dance_activate_toggle == 1 and self.previous_dance_activate_toggle == 0)

        shutdown_toggle = self.input_joystick["triangle"]
        self.joystick_cmd.shutdown_signal = shutdown_toggle

        activate_toggle = self.input_joystick["L1"]
        self.joystick_cmd.activate_event = (activate_toggle == 1 and self.previous_activate_toggle == 0)

        dance_toggle = self.input_joystick["L2"]
        self.joystick_cmd.dance_switch_event = (dance_toggle == 1 and self.previous_dance_switch_toggle != 1)

        gait_switch_toggle = self.input_joystick["R2"]
        self.joystick_cmd.gait_switch_event = (gait_switch_toggle == 1 and self.previous_gait_switch_toggle != 1)

        # Update previous values for toggles and state
        self.previous_gait_toggle = gait_toggle
        self.previous_hop_toggle = hop_toggle
        self.previous_activate_toggle = activate_toggle
        self.previous_dance_activate_toggle = dance_activate_toggle

        self.previous_dance_switch_toggle = dance_toggle
        self.previous_gait_switch_toggle = gait_switch_toggle

        ####### Handle continuous commands ########
        x_vel = self.input_joystick["ly"] * self.config.max_x_velocity
        y_vel = self.input_joystick["lx"] * -self.config.max_y_velocity
        self.joystick_cmd.horizontal_velocity = np.array([x_vel, y_vel])
        self.joystick_cmd.yaw_rate = self.input_joystick["rx"] * -self.config.max_yaw_rate

        message_rate = self.input_joystick["message_rate"]
        message_dt = 1.0 / message_rate

        pitch = self.input_joystick["ry"] * self.config.max_pitch
        deadbanded_pitch = Utilities.deadband(
            pitch, self.config.pitch_deadband
        )
        pitch_rate = Utilities.clipped_first_order_filter(
            state.pitch,
            deadbanded_pitch,
            self.config.max_pitch_rate,
            self.config.pitch_time_constant,
        )
        self.joystick_cmd.pitch = state.pitch + message_dt * pitch_rate

        height_movement = self.input_joystick["dpady"]
        self.joystick_cmd.height = state.height - message_dt * self.config.z_speed * height_movement

        roll_movement = - self.input_joystick["dpadx"]
        self.joystick_cmd.roll = state.roll + message_dt * self.config.roll_speed * roll_movement
        
        return self.joystick_cmd

    def set_color(self, color):
        self.joystick.led_color(**color)
