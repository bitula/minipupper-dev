from controller.module import BaseModule
from .LCD.ST7789 import ST7789
import numpy as np
from PIL import Image


class Interface(BaseModule):
    LCD_POWER_GPIO = "/sys/class/gpio/gpio26/value"
    
    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)
        
        self.display = ST7789()


    def on_start(self):
        self.set_lcd_enable(1)
        self.display.begin()
        self.display.clear()

    
    def on_tick(self):
        if self.shm_read("DisplayIO", "draw_image"):
            img = np.array(self.shm_numpy_in("DisplayIO").image)
            _img = Image.fromarray(img.reshape(320, 240, 3))
            self.display.display(_img)

    
    def on_stop(self):
        self.set_lcd_enable(0)


    def chk_lcd(self):
        _path = self.cfg.GPIO + "/gpio26/direction"
        if not self.chk_rw_access(_path, ro=True):
            return False
        if not self.chk_direction(_path):
            return False
        
        if not self.chk_rw_access(self.cfg.GPIO + "/gpio26/value"):
            return False

        if not self.chk_rw_access("/dev/spidev0.0"):
            return False
        if not self.chk_rw_access("/dev/mem"):
            return False
        if not self.chk_rw_access("/dev/gpiomem"):
            return False

        return True


    def set_lcd_enable(self, flag: int):
        with open(self.LCD_POWER_GPIO, "w") as f:
           f.write(str(flag))