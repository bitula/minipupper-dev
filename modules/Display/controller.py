import os
import numpy as np

from controller.module import BaseModule
from PIL import Image


class Controller(BaseModule):
    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)

        dir_path  = os.path.dirname(__file__)
        repo_path = os.path.abspath(os.path.join(dir_path, '../..'))
        # TODO implement autoimport for assets
        # traverse assets directory and build dict for all assets 
        # ending with png for images, not sure about animations
        self.assets_path = repo_path + "/assets/cartoons/"
        
        image_shm = self.shm_numpy_out("DisplayIO").image
        self.shmout_image = np.frombuffer(image_shm, dtype=np.uint8)

        self.draw_state = 0
        self.draw_image = False

    
    def on_start(self):
        self.draw_state = 1
        self.draw_write("logo.png")
    
    
    def on_tick(self):
        # TODO improve controll for draw writes
        if self.shmem_out.DisplayIO[0].draw_image:
            self.shm_write("DisplayIO", "draw_image", False)

        if self.shm_read("SensorsIO", "enable") and self.draw_state != 0:
            self.draw_state = 0
            self.draw_write("walk.png")
            
        if not self.shm_read("SensorsIO", "enable") and self.draw_state != 1:
            self.draw_state = 1
            self.draw_write("logo.png")


    def draw_write(self, name):
        image = Image.open(self.assets_path + name)
        image.resize((320,240))
        self.shmout_image[:] = np.array(image).flatten()
        self.shm_write("DisplayIO", "draw_image", True)