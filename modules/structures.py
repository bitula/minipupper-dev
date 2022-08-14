from ctypes import Structure, c_double, c_bool, c_float, c_int, c_uint8


class HardwareIO(Structure):
    _fields_ = [
        ("board_enable", c_bool),
        ("battery_power", c_bool),
        ("supply_voltage", c_int),
        ("is_calibrated", c_bool),
        ("set_calibration", c_bool),
        ('calibrated_angles', c_double*12),
        ]


class SensorsIO(Structure):
     _fields_ = [
        ("enable", c_bool),
        ('velx', c_float),
        ('vely', c_float),
        ('yaw', c_float), 
        ('roll', c_float),
        ('pitch', c_float),
        ('height', c_float),
        ('hop', c_bool),
        ('trot', c_bool),
        ('dance', c_bool),
        ('dance_switch', c_bool),
        ('gait_switch', c_bool),
        ]


# TODO added high level commandsIO (move_to, ...)


class ActuatorsIO(Structure):
    _fields_ = [
        ("pwm_enable", c_bool),             # not implemented, pwm should be disbaled when not in use ?
        ("update_legs", c_bool),            # should be off if board false
        ('joint_angles', c_double*12), 
        ]


class DisplayIO(Structure):                 # should be off if board false
    _fields_ = [
        ("lcd_enable", c_bool),          
        ("draw_image", c_bool),
        ("image", c_uint8*230400)
    ]