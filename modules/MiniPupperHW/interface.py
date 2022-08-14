import numpy as np

from controller.module import BaseModule
from controller.utilities import chk_rw_access, chk_direction


class Interface(BaseModule):
    POWER_GPIO     = np.array([21, 25])
    GPIO           = "/sys/class/gpio/"
    NVMEM          = "/sys/bus/nvmem/devices/3-00501/nvmem"
    BATTERY        = "/sys/class/power_supply/max1720x_battery/voltage_now"
    BATTERY_CHK    = 3
    BTR_MIN_VOLTS  = 6500
    
    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)
        
        self.battery_monitor = True

        calib_angles = self.shm_numpy_out("HardwareIO").calibrated_angles
        self.shmout_calib_angles = np.frombuffer(calib_angles, dtype=np.float64).reshape(3, 4)
        self.shm_write("HardwareIO", "is_calibrated",  False)
        self.chk_ok = None
        self.get_angles_eeprom() # FIXME issue with on_start order


    def on_start(self) -> None:
        # add config argument, to enable/disable battery monitor ?

        self.chk_battery() # TODO implement access check
        
        self.chk_ok = self.chk_board()
        if not self.chk_ok:
            self.shutdown()
            return
        self.set_board_enable(1)

       
    def on_tick(self) -> None:
        # TODO implement calibration angles set
        # print(self.shmem_out.HardwareIO[0].board_enable)
        if not self.battery_monitor:
            self.timeout(self.BATTERY_CHK)
            return

        volts = self.get_voltage()
        self.shm_write("HardwareIO", "supply_voltage", volts)

        if volts < 5001: # wrong way to detect if battery is connected ?
            self.shm_write("HardwareIO", "battery_power", False)
            print(" minipupper connected to power supply")
            self.battery_monitor = False
            print(" battery monitoring is shutdown")

        elif 5001 <= volts <= self.BTR_MIN_VOLTS:
            self.set_board_enable(0)
            print("battery charge:", volts)

        self.timeout(self.BATTERY_CHK)

    def on_stop(self) -> None:
        if not self.chk_ok:
            return
        self.set_board_enable(0)


    def chk_battery(self):
        return chk_rw_access(self.BATTERY, ro=True)


    def get_voltage(self):
        try:
            with open(self.BATTERY, "r") as f:
                return(int(f.read()[:-1]))
        except Exception as e:
            print("battery error:", e)
            return False
        

    def chk_board(self):
        for n in self.POWER_GPIO:
            _path = self.GPIO + "/gpio" + str(n) + "/direction"
            if not chk_rw_access(_path, ro=True):
                return False
            if not chk_direction(_path):
                return False

            if not chk_rw_access(self.GPIO + "/gpio" + str(n) + "/value"):
                return False

        return True
        

    def set_board_enable(self, flag: bool):     
        for n in self.POWER_GPIO:
            _path = self.GPIO + "/gpio" + str(n) + "/value"
            with open(_path, "w") as f:
                f.write(str(flag))

        self.shm_write("HardwareIO", "board_enable", flag)


    def get_angles_eeprom(self):
        filepath = self.NVMEM
        print("getting calibration")
        # TODO Store and Restore from json with checksum
        try:
            with open(filepath, "rb") as nvmem:
                # in case parsing will fail
                try:   
                    _list = [
                        [int(i) for i in next(nvmem)[:-2].decode("utf-8").replace(" ", "").split(",")]
                        for x in range(3)
                        ]
                    
                    # print(_list)
                    self.shmout_calib_angles[:] = np.array(_list) * np.pi / 180.0
                    self.shm_write("HardwareIO", "is_calibrated",  True)
                except:
                    print("failed to parse calibration data from:", filepath)
        
        except Exception as e:
            print("failed to load calibration values from nvmem: {1}".format(e))


    ### calibration agles set
    # def set_angles_eeprom(self):

    #     # TODO remove nested for loop
    #     buf_matrix = np.zeros((3, 4))
    #     for i in range(3):
    #         for j in range(4):
    #             buf_matrix[i,j]= self.NEUTRAL_DEG[i,j]

    #     _tmp = str(buf_matrix)
    #     _tmp = _tmp.replace('.' , ',')
    #     _tmp = _tmp.replace('[' , '')
    #     _tmp = _tmp.replace(']' , '')
    #     _tmp += '\n'

    #     ### removed unused bits from eeprom)
    #     expected_len = len(str.encode(_tmp))

    #     with open(self.NVMEM, "rb") as f:
    #         calib_bytes  = f.read()
    #         print(calib_bytes[:62]) # for backup

    #     print(calib_bytes[62:63])
    #     ### eeprom earse all data
    #     if calib_bytes[expected_len:expected_len+1] == b'\xff':
    #         with open(self.NVMEM, "wb") as f:
    #             f.write(b'\0'*(1024))

    #     ### restore calib bytes
    #     with open(self.NVMEM, "wb") as f:
    #         f.write(calib_bytes[:expected_len])
        
    #     with open(self.NVMEM, "wb") as f:
    #         f.write(str.encode(_tmp))
    #         # f.write(b'  0, -32,   9,  18,\n  47,  72,  29,  65,\n -56, -90, -22, -68,\n')
