try:
    from pynput import keyboard, mouse
    from pynput.keyboard import KeyCode
except ImportError:
    # TODO import sshkeyboard
    pass

import subprocess
from controller.module import BaseModule


class KeyboardMouseEvents:
    def __init__(self):
            self.mouse_possition_x = 0.
            self.mouse_possition_y = 0.
            self.mouse_scroll_dy = 0.
            self.mouse_left_clk = False
            self.mouse_right_clk = False
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


class Interface(BaseModule):
    
    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)

        # TODO should use windows size and detect when mouse if over
        display = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
        display = display.decode("utf-8")
        display  = display[:-1].split('x')
        
        self.display_width = float(display[0])
        self.display_hight = float(display[1])

        self.m_scroll_state = 0

        self.mouse_events = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)

        self.keyboard_events  = keyboard.Listener(
            on_press=self.on_press, 
            on_release=self.on_release)

        self.events = KeyboardMouseEvents()

    def on_start(self):
        self.shm_write("SensorsIO", None, (0, 0, 0, 0, 0, 0, 0, 0, 0))
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
            self.events.mouse_left_clk = pressed

        if button == mouse.Button.right:
            self.events.mouse_right_clk = pressed


    def on_scroll(self, x, y, dx, dy):
        self.events.mouse_scroll_dy += dy
        # print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up',(x, y)))


    def on_press(self, key):
        # press
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

        # toggle
        if key == KeyCode.from_char('1'):
            self.events.toggle_1 = not self.events.toggle_1

        if key == KeyCode.from_char('2'):
            self.events.toggle_2 = not self.events.toggle_2

        if key == KeyCode.from_char('3'):
            self.events.toggle_3 = not self.events.toggle_3

        if key == KeyCode.from_char('4'):
            self.events.toggle_4 = not self.events.toggle_4

        if key == KeyCode.from_char('5'):
            self.events.toggle_5 = not self.events.toggle_5

        if key == keyboard.Key.space:
            self.events.toggle_space = not self.events.toggle_space

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

    
    def on_tick(self):

        # reset memmory
        self.shm_write("SensorsIO", None, (0, 0, 0, 0, 0, 0, 0, 0, 0))

        self.shm_write("SensorsIO", "enable", self.events.toggle_space)

        if self.events.w_pressed:
            self.shm_write("SensorsIO", "velx", self.events.mouse_possition_x)
            self.shm_write("SensorsIO", "vely",self.events.mouse_possition_y)

        # TODO add A, S, D keys
        
        if self.events.alt_l_pressed:
            self.shm_write("SensorsIO", "yaw", self.events.mouse_possition_x)
            self.shm_write("SensorsIO", "pitch", self.events.mouse_possition_y)

        if self.m_scroll_state == self.events.mouse_scroll_dy:
            self.events.mouse_scroll_dy = 0
        else:
            self.m_scroll_state = self.events.mouse_scroll_dy

        if self.events.shift_l_pressed:
            # TODO add +/- keys
            self.shm_write("SensorsIO", "height", self.events.mouse_scroll_dy)

        if self.events.ctrl_l_pressed:
            # TODO add +/- keys
            self.shm_write("SensorsIO", "roll", self.events.mouse_scroll_dy)

        if self.events.toggle_1:
            self.shm_write("SensorsIO", "trot", self.events.self.events.toggle_1)

        if self.events.toggle_2:
            self.shm_write("SensorsIO", "hop", self.events.self.events.toggle_2)
            
        if self.events.toggle_3:
            self.shm_write("SensorsIO", "gait_switch", self.events.self.events.toggle_3)

        if self.events.toggle_4:
            self.shm_write("SensorsIO", "dance", self.events.self.events.toggle_4)

        if self.events.toggle_5:
            self.shm_write("SensorsIO", "dance_switch", self.events.self.events.toggle_5)

