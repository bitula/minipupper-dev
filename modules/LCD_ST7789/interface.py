from controller.module import BaseModule
from controller.utilities import chk_rw_access, chk_direction
from .LCD.ST7789 import ST7789
import numpy as np
from PIL import Image


class Interface(BaseModule):
    LCD_POWER_GPIO = "/sys/class/gpio/gpio26"
    
    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)
        
        self.display = ST7789()
        self.chk_ok = False


    def on_start(self):
        self.chk_ok = self.chk_lcd()
        if not self.chk_ok:
            self.exit()
            return

        self.set_lcd_enable(1)
        self.display.begin()
        self.display.clear()

    
    def on_tick(self):
        if self.shm_read("DisplayIO", "draw_image"):
            img = np.array(self.shm_numpy_in("DisplayIO").image)
            _img = Image.fromarray(img.reshape(320, 240, 3))
            self.display.display(_img)

    
    def on_stop(self):
        if self.chk_ok:
            self.set_lcd_enable(0)


    def chk_lcd(self):
        chk = True
        _path = self.LCD_POWER_GPIO + "/direction"
        if not chk_rw_access(_path, ro=True):
            chk = False
        if not chk_direction(_path):
            chk = False
        
        if not chk_rw_access(self.LCD_POWER_GPIO + "/value"):
            chk = False

        # if not chk_rw_access("/dev/spidev0.0"):
        #     chk = False
        # if not chk_rw_access("/dev/mem"):
        #     chk = False
        # if not chk_rw_access("/dev/gpiomem"):
        #     chk = False

        return chk


    def set_lcd_enable(self, flag: int):
        with open(self.LCD_POWER_GPIO + "/value", "w") as f:
           f.write(str(flag))