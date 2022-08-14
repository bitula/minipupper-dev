import os
import numpy as np

from controller.module import BaseModule
from controller.utilities import chk_rw_access


class Interface(BaseModule):
    LEGS_PWM       = np.array([[15, 12, 9, 6], [14, 11, 8, 5], [13, 10, 7, 4]])
    PWM_PERIOD     = 4000000
    NEUTRAL_PWM    = 1500
    NEUTRAL_DEG    = np.array([[0, 0, 0, 0], [45, 45, 45, 45], [-45, -45, -45, -45]])
    NEUTRAL_RADS   = NEUTRAL_DEG * np.pi / 180.0
    MULTIPLIERS    = np.array([[1, 1, -1, -1], [-1, 1, -1, 1], [-1, 1, -1, 1]])
    MACROS_RAD     = 11.111 * 180.0 / np.pi
    PWMCHIP        = "/sys/class/pwm/pwmchip0"

    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)

        self.calibrated_rads = self.NEUTRAL_RADS
        self.legs_to_pwm_index = []

    def on_start(self):
        if self.shm_read("HardwareIO", "is_calibrated"):
            calibrated_rads = self.shm_numpy_in("HardwareIO").calibrated_angles
            self.calibrated_rads = np.array(calibrated_rads[:]).reshape(3, 4)
            print("calibrated rads\n", self.calibrated_rads)
        
        chk_pwm = self.chk_pwm()
        if not chk_pwm:
            self.shutdown()
            return

        # TODO remove nested for loop
        for leg_index in range(4):
            for axis_index in range(3):
                pwm_id = self.LEGS_PWM[axis_index, leg_index]
                pwm_path = self.PWMCHIP + "/pwm" + str(pwm_id) + "/duty_cycle"
                self.legs_to_pwm_index.append([[axis_index, leg_index], pwm_path])
    
        self.set_legs_enable(1)
        self.set_legs_pwms(self.NEUTRAL_RADS)

    def on_tick(self) -> None:
        if not self.shm_read("ActuatorsIO", "update_legs"):
            return

        _joint_angles = self.shm_read("ActuatorsIO", "joint_angles")
        joint_angles = np.array(_joint_angles[:]).reshape(3, 4)
        # print(joint_angles)
        self.set_legs_pwms(joint_angles)

    def on_stop(self):
        # no need board disables servos
        # self.set_legs_enable(0) 
        pass

    def chk_pwm(self):
        path = self.PWMCHIP
        if not os.path.exists(path):
            print("error: path {0} does not exist, looks like pwmchip is not intialized".format(path))
            return False
        
        # check premissions
        for n in range(15):
            pwm_path = path + "/pwm" + str(n)
            period = pwm_path + "/period"

            if chk_rw_access(period, ro=True):
                with open(period, "r") as f:
                    period = int(f.read()[:-1])
                    if period != self.PWM_PERIOD:
                        print(period, period)
                        print("error: pwm period value is not expected value of 400000")
                        return False
            else:
                return False

            _path = pwm_path + "/enable"
            if not chk_rw_access(_path):
                return False

            _path = pwm_path + "/duty_cycle"
            if not chk_rw_access(_path):
                return False
        
        return True

    def set_legs_enable(self, flag: int):
        # TODO should go into sleep position before shutdown
        _list = self.legs_to_pwm_index
        for n in range(len(_list)):
            pwm = _list[n][1]
            path = pwm[:-10] + "enable"
            # print(path, flag)
            with open(path, "w") as f:
                f.write(str(flag))

    def set_legs_pwms(self, joint_angles):
        _list = self.legs_to_pwm_index
        for n in range(len(_list)):
            axis = _list[n][0][0]
            leg = _list[n][0][1]
            pwm = _list[n][1]

            joint_angle = joint_angles[axis, leg]
            neutral_angle = self.calibrated_rads[axis, leg] 
            multiplier =  self.MULTIPLIERS[axis, leg]
            # pre-computer more values ?
            angle_deviation = ( joint_angle - neutral_angle ) * multiplier 
            _cycle = (self.NEUTRAL_PWM + self.MACROS_RAD * angle_deviation) * 1e3
            # print(pwm, str(int(_cycle)))
            with open(pwm, "w") as f:
                f.write(str(int(_cycle)))