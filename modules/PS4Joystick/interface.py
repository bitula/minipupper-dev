from controller.module import BaseModule
from .PS4Joystick import Joystick


class Interface(BaseModule):
    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)

        self.joystick = None
        self.joystick_error = 0

        self.lx = 0.
        self.ly = 0.
        self.rx = 0.
        self.ry = 0.
        self.l1 = [False, False]
        self.l2 = [False, False]
        self.r1 = [False, False]
        self.r2 = [False, False]
        self.cross = [False, False]
        self.square = [False, False]
        self.circle = [False, False]
        self.triangle = [False, False]


    def on_start(self):
        try:
            self.joystick = Joystick()
        except KeyboardInterrupt:
            pass


    def on_tick(self):
        if self.joystick_error > 15:
            print("Joystic Connection Error")
            del self.joystick
            self.joystick = Joystick()
            self.joystick_error = 0
            return
        
        try:
            values = self.joystick.get_input()
            self.joystick_error = 0
            # TODO add battery check, if low reset values and disable
        except:
            # does not seem to be triggered
            print("Joystic Input Error")
            return
        else:
            if values is None:
                self.joystick_error += 1
                print("Joystic Low Signal Warning")
                return

        dpadx = values["dpad_right"] - values["dpad_left"]
        dpady = values["dpad_up"] - values["dpad_down"]

        left_1 = values["button_l1"]
        if left_1 and left_1 != self.l1[0]:
            self.l1[1] = not self.l1[1]
            self.shm_write("SensorsIO", "enable", self.l1[1])

        left_2 = values["button_l2"]
        if left_2 and left_2 != self.l2[0]:
            self.l2[1] = not self.l2[1]
            self.shm_write("SensorsIO", "dance_switch", self.l2[1])
        
        right_1 = values["button_r1"]
        if right_1 and right_1 != self.r1[0]:
            self.r1[1] = not self.r1[1]
            self.shm_write("SensorsIO", "trot", self.r1[1])

        right_2 = values["button_r2"]
        if right_2 and right_2 != self.r2[0]:
            self.r2[1] = not self.r2[1]
            self.shm_write("SensorsIO", "gait_switch", self.r2[1])

        cross = values["button_cross"]
        if cross and cross != self.cross[0]:
            self.cross[1] = not self.cross[1]
            self.shm_write("SensorsIO", "hop", self.cross[1])
            
        circle = values["button_circle"]
        if circle and circle != self.circle[0]:
            self.circle[1] = not self.circle[1]
            self.shm_write("SensorsIO", "dance", self.circle[1])

        self.shm_write("SensorsIO", "yaw", values["right_analog_x"])        
        self.shm_write("SensorsIO", "pitch", -values["right_analog_y"])     

        self.shm_write("SensorsIO", "height", dpady)                        
        self.shm_write("SensorsIO", "roll", dpadx)

        self.shm_write("SensorsIO", "velx", -values["left_analog_y"]) 
        self.shm_write("SensorsIO", "vely", values["left_analog_x"])
        
        self.l1[0] = values["button_l1"]
        self.l2[0] = values["button_l2"]
        self.r1[0] = values["button_r1"]
        self.r2[0] = values["button_r2"]
        self.cross[0] = values["button_cross"]
        self.circle[0] = values["button_circle"]

    # TODO add color for enable/disable
    def set_color(self, color):
        self.joystick.led_color(**color)


# Joystick values dump
# {
#   "left_analog_x": 0.2313725490196079,            FIXME not 0 on connect
#   "left_analog_y": 0.0039215686274509665,
#   "right_analog_x": 0.0,
#   "right_analog_y": 0.0,
#   "l2_analog": -1.0,                              # -1,1 defualt -1
#   "r2_analog": -1.0,
#   "dpad_up": false,
#   "dpad_down": false,
#   "dpad_left": false,
#   "dpad_right": false,
#   "button_cross": false,
#   "button_circle": false,
#   "button_square": false,
#   "button_triangle": false,
#   "button_l1": false,
#   "button_l2": false,
#   "button_l3": false,
#   "button_r1": false,
#   "button_r2": false,
#   "button_r3": false,
#   "button_share": false,
#   "button_options": false,
#   "button_trackpad": false,
#   "button_ps": false,
#   "motion_y": -15,
#   "motion_x": -5,
#   "motion_z": -16,
#   "orientation_roll": 211,
#   "orientation_yaw": 7961,
#   "orientation_pitch": 1227,
#   "trackpad_touch0_id": 0,
#   "trackpad_touch0_active": false,
#   "trackpad_touch0_x": 0,
#   "trackpad_touch0_y": 0,
#   "trackpad_touch1_id": 0,
#   "trackpad_touch1_active": false,
#   "trackpad_touch1_x": 0,
#   "trackpad_touch1_y": 0,
#   "timestamp": 1,
#   "battery": 4,
#   "plug_usb": false,
#   "plug_audio": false,
#   "plug_mic": false
# }