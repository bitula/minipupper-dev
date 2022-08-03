#!/usr/bin/env python
from imaplib import Commands
from re import U
import sys
import os
dir_path  = os.path.dirname(__file__)
repo_path = os.path.abspath(os.path.join(dir_path, '../..'))
sys.path.insert(0, repo_path)

from pynput import keyboard, mouse
from pynput.keyboard import KeyCode
import subprocess
import time
import numpy as np

from drivers.Servos.HardwareInterface import HardwareInterface
from drivers.Servos.Config import Configuration

from modules.controller import Controller
from modules.controller import MovementGroup
from modules.controller.MovementScheme import MovementScheme # TODO fix import
from modules.controller import Kinematics
from modules.controller import State
from modules.controller import Command
from modules.controller import Utilities


QUAD_ORIENTATION = np.array([1, 0, 0, 0])

class KeyboardMouseEvents:
    def __init__(self):
            self.mouse_possition_x = 0.
            self.mouse_possition_y = 0.
            self.mouse_scroll_dy = 0
            self.button_left = False
            self.button_right = False
            self.w_pressed = False
            self.s_pressed = False
            self.a_pressed = False
            self.d_pressed = False
            self.alt_l_pressed = False
            self.shift_l_pressed = False
            self.ctrl_l_pressed = False
            self.toggle_1 = False
            self.toggle_2 = False
            self.toggle_3 = False
            self.toggle_4 = False
            self.toggle_5 = False
            self.toggle_space = False


class KeyboardMouseInterface:
    def __init__(self):

        display = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
        display = display.decode("utf-8")
        display  = display[:-1].split('x')
        
        self.display_width = float(display[0])
        self.display_hight = float(display[1])

        self.events = KeyboardMouseEvents()

        self.m_scroll_state = 0
        
        self.mouse_events = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)

        self.keyboard_events  = keyboard.Listener(
            on_press=self.on_press, 
            on_release=self.on_release)

        self.mouse_events.start()
        self.keyboard_events.start()

    def on_move(self, x, y):
        """
        Range is from -1 to +1 adjusted to screen resolation
        Screen center is 0,0
        End of left side of a screen equals to -1 on x axis
        Bottom of screen equals to -1 on y axis
        """
        self.events.mouse_possition_x = ( 0.5 - x / self.display_width ) * -2.0
        self.events.mouse_possition_y = (0.5 - y / self.display_hight) * 2 

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.events.button_left = pressed

        if button == mouse.Button.right:
            self.events.button_right = pressed

    def on_scroll(self, x, y, dx, dy):
        self.events.mouse_scroll_dy += dy
        # print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up',(x, y)))

    def on_press(self, key):
        # TODO bitmask
        if key  == KeyCode.from_char('w'):
            self.events.w_pressed = True

        if key == KeyCode.from_char('a'):
            self.events.a_pressed = True

        if key == KeyCode.from_char('s'):
            self.events.s_pressed = True

        if key == KeyCode.from_char('d'):
            self.events.d_pressed = True

        if key == keyboard.Key.alt_l:
            self.events.alt_l_pressed = True

        if key == keyboard.Key.shift_l:
            self.events.shift_l_pressed = True

        if key == keyboard.Key.ctrl_l:
            self.events.ctrl_l_pressed = True

        if key == KeyCode.from_char('1'):
            if self.events.toggle_1:
                self.events.toggle_1 = False
            else:
                self.events.toggle_1 = True

        if key == KeyCode.from_char('2'):
            if self.events.toggle_2:
                self.events.toggle_2 = False
            else:
                self.events.toggle_2 = True

        if key == KeyCode.from_char('3'):
            if self.events.toggle_3:
                self.events.toggle_3 = False
            else:
                self.events.toggle_3 = True

        if key == KeyCode.from_char('4'):
            if self.events.toggle_4:
                self.events.toggle_4 = False
            else:
                self.events.toggle_4 = True

        if key == KeyCode.from_char('5'):
            if self.events.toggle_5:
                self.events.toggle_5 = False
            else:
                self.events.toggle_5 = True

        if key == keyboard.Key.space:
            if self.events.toggle_space:
                self.events.toggle_space = False
            else:
                self.events.toggle_space = True

    def on_release(self, key):
        if key == KeyCode.from_char('w'):
            self.events.w_pressed = False

        if key == KeyCode.from_char('a'):
            self.events.a_pressed = False

        if key == KeyCode.from_char('s'):
            self.events.s_pressed = False

        if key == KeyCode.from_char('d'):
            self.events.d_pressed = False

        if key == keyboard.Key.alt_l:
            self.events.alt_l_pressed = False

        if key == keyboard.Key.shift_l:
            self.events.shift_l_pressed = False

        if key == keyboard.Key.ctrl_l:
            self.events.ctrl_l_pressed = False
    
    def input_events(self):
        
        if self.m_scroll_state == self.events.mouse_scroll_dy:
            self.events.mouse_scroll_dy = 0
        else:
            self.m_scroll_state = self.events.mouse_scroll_dy
        
        return self.events

def stance_controller(x: float, y:float, dt: float, state: State, config: Configuration):
    
    yaw = x * -config.max_yaw_rate

    pitch = y * config.max_pitch
    deadbanded_pitch = Utilities.deadband(pitch, config.pitch_deadband)
    pitch_rate = Utilities.clipped_first_order_filter(
        state.pitch,
        deadbanded_pitch,
        config.max_pitch_rate,
        config.pitch_time_constant,
    )
    pitch = state.pitch + dt * pitch_rate
    
    return yaw, pitch


def minipupper_cmds(cmds: Command.Command, uinput: KeyboardMouseEvents, state: State, config: Configuration):

    cmds.tick_reset()
    
    # TODO should be in config
    # Not sure why it is different
    message_dt = 0.02

    ### activate/diactive robot control
    ### L1
    if uinput.toggle_space:
        cmds.activate_event = uinput.toggle_space
        uinput.toggle_space = False

    # TODO add delta to on_move might not work corectly
    # without delta, stance controller does not work correctly
    if uinput.alt_l_pressed:
        cmds.yaw_rate, cmds.pitch = stance_controller(
            uinput.mouse_possition_x, 
            uinput.mouse_possition_y, 
            message_dt, 
            state, 
            config)

    ### Movment Hight
    if uinput.shift_l_pressed:
        cmds.height = state.height - message_dt * config.z_speed * uinput.mouse_scroll_dy

    ### Movment Roll
    if uinput.ctrl_l_pressed:
        cmds.roll = state.roll + message_dt * config.roll_speed * uinput.mouse_scroll_dy
    
    ### R1
    if uinput.toggle_1:
        cmds.trot_event = uinput.toggle_1
        uinput.toggle_1 = False

    ### X
    if uinput.toggle_2:
        cmds.hop_event = uinput.toggle_2
        uinput.toggle_2 = False
        
    ### R2
    if uinput.toggle_3:
       cmds.gait_switch_event = uinput.toggle_3
       uinput.toggle_3 = False

    ### Circle
    if uinput.toggle_4:
        cmds.dance_activate_event = uinput.toggle_4
        uinput.toggle_4 = False 

    ### L2
    if uinput.toggle_5:
       cmds.dance_switch_event = uinput.toggle_5
       uinput.toggle_5 = False

    ### Movement Velocity
    # w = x_vel = 0.2 
    # s = x_vel = -0.2
    # a = y_vel = 0.2   # mouse_x left 
    # d = y_vel = -0.2  # mouse_x right

    # d = yaw_rate = 0.2 
    # a = yaw_rate = -0.2

    # TODO does not work correctly.
    if uinput.w_pressed:
        x_vel = uinput.mouse_possition_y * config.max_x_velocity
        y_vel = uinput.mouse_possition_x * -config.max_y_velocity
        cmds.horizontal_velocity = np.array([x_vel, y_vel])

    # if uinput.s_pressed:
    #     x_vel = uinput.mouse_possition_y * config.max_x_velocity
    #     y_vel = uinput.mouse_possition_x * -config.max_y_velocity
    #     cmds.horizontal_velocity = np.array([x_vel, y_vel])

    if uinput.d_pressed:
        cmds.yaw_rate = uinput.mouse_possition_y * -config.max_yaw_rate

    # Same as D  
    # if uinput.a_pressed:
    #     cmds.yaw_rate = uinput.mouse_possition_y * -config.max_yaw_rate
    
    return cmds



def main():

    UserInput = KeyboardMouseInterface()

    # Create config
    commands = Command.Command()
    config = Configuration()
    hardware_interface = HardwareInterface()

    #Create movement group scheme
    moves_list = []
    MovementGroup.appendDanceMovement(moves_list)
    movement_ctl = MovementScheme(moves_list)

    # Create controller and user input handles
    controller = Controller.Controller(
        config,
        Kinematics.four_legs_inverse_kinematics,
    )
    state = State.State()
    state.quat_orientation = QUAD_ORIENTATION

    print("Summary of gait parameters:")
    print("overlap time: ", config.overlap_time)
    print("swing time: ", config.swing_time)
    print("z clearance: ", config.z_clearance)
    print("x shift: ", config.x_shift)

    # Wait until the activate button has been pressed
    while True:

        print("Press space bar to activate/diactivate robot control")
        
        while True:

            input_events = UserInput.input_events()
            cmds = minipupper_cmds(commands, input_events, state, config)

            if cmds.activate_event:
                break

            time.sleep(0.1)
        
        print("Robot activated.")
        
        while True:

            input_events = UserInput.input_events()  
            cmds = minipupper_cmds(commands, input_events, state, config)
            
            if cmds.activate_event:
                break

            # movement scheme
            movement_switch = cmds.dance_switch_event
            gait_state = cmds.trot_event
            dance_state = cmds.dance_activate_event

            # gait and movement control
            if gait_state == True or dance_state == True:
                # if triger tort event, reset the movement number to 0       
                movement_ctl.resetMovementNumber()
                
            movement_ctl.runMovementScheme(movement_switch)
            food_location = movement_ctl.getMovemenLegsLocation()
            attitude_location = movement_ctl.getMovemenAttitude()
            robot_speed = movement_ctl.getMovemenSpeed()

            controller.run(state, cmds, food_location, attitude_location, robot_speed)

            # Update the pwm widths going to the servos
            hardware_interface.set_actuator_postions(state.joint_angles)
           

            # print(cmds.__dict__)

            time.sleep(config.dt)

try:
    # subprocess.run(["stty", "-echo"])
    main()
except KeyboardInterrupt:
    # subprocess.run(["stty", "echo"])
    pass


