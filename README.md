# MINIPUPPER-DEV

This is unofficial and early work in progress to (re)organize and "refactor" [MangDang's QuadrupedRobot](https://github.com/mangdangroboticsclub/QuadrupedRobot.git) repository.

The branch is not even version version 0, it is highly experimental, there is still much work to be done.

## Notible changes from original code base
  - All services are removed and replaced with udev rules
  - Each module can be run as subprocess, or thread, or be executed in main process
  - Display and Servos are only enabled when pupperctl.py is running
  - Code is organized into modules that are futher broken down into controllers and interfaces
  - Pupperctl application can be started from any where with modules arguments
  - Python pip packages are installed and run as non-root user sudo is not required when starting pupperctl.py
  - UDPComms is completelly removed
  - Drivers installion scripts are removed and moved to makefiles
  - No need to connect network cable or monitor and keyboard/mouse to minipupper's RPi
  - Default Ubuntu image boot drive should be edited before first time boot to setup network and hardware
  - To save some RAM snap is completelly removed by defualt (it is optional)
  - EEPROM only stores calibration values all other bits are removed
  - EEPROM backup and restore script using rsync
  - TigerVNC Xfce4 remote desktop, as optinal install requeires TigerVNC Xfce4

## Known Limitations
- pupperctl.py does not launch on boot, battery serivce will only work when script is running.
- Modules running as threads or in main will not properlly shutdown
- Deamon when started might fail to stop existing process(es)
- Incomplete implemenation of Config.py and args parser
- Joystick and Keyboard input is not well tested
- Kinematics modules might have bugs, specifically related to time delta
- Joystick at random times will fail to connect first time (driver issue, hard to isolate)
- When debuging, vscode will not start ssh with x forwarding, on debug stop pupperctl does not exit cleanly
- Calibration UI is not implemented with storing clibration done is not implemented

### Getting started
To setup microSD from scratch see [INSTALL](INSTALL.md), the pupperctl will work with existing installation.

Disable battery systemd service, because it might result in read errors if both are running.
```console
sudo systemd 

```console
ubuntu@minipupper~$ sudo systemctl stop battery_monitor.service
ubuntu@minipupper~$ git clone https://github.com/bitula/minipupper-dev
ubuntu@minipupper~$: minipupper-dev/pupperctl.py --joystick
interfaces default hardware
 shared memory ActuatorsIO intialized
 shared memory HardwareIO intialized
interfaces default actuators
controllers default actuators
 shared memory SensorsIO intialized
interfaces default display
 shared memory DisplayIO intialized
controllers default display
interfaces default speaker
controllers default speaker
interfaces default joystick
getting calibration
 int:def:hardware:MiniPupperHW initilized
 int:def:actuators:MiniPupperLegs initilized
 con:def:actuators:Kinematics initilized
 int:def:display:LCD_ST7789 initilized
 con:def:display:Display initilized
 int:def:speaker:BaseModule initilized
 con:def:speaker:BaseModule initilized
 int:def:joystick:PS4Joystick initilized
 controller started with PID(s): 17623
 int:def:speaker:BaseModule subprocess starting
 int:def:hardware:MiniPupperHW subprocess starting
 minipupper connected to power supply
 battery monitoring is shutdown
 int:def:display:LCD_ST7789 subprocess starting
 int:def:actuators:MiniPupperLegs subprocess starting
calibrated rads
 [[ 0.         -0.55850536  0.15707963  0.31415927]
 [ 0.82030475  1.25663706  0.50614548  1.13446401]
 [-0.97738438 -1.57079633 -0.38397244 -1.18682389]]
 int:def:joystick:PS4Joystick subprocess starting
 con:def:display:Display subprocess starting
 con:def:speaker:BaseModule subprocess starting
 con:def:actuators:Kinematics subprocess starting
[info][controller 1] Created devices /dev/input/js0 (joystick) /dev/input/event2 (evdev) 
[info][bluetooth] Scanning for devices
```
Press Ctl+C to stop

### Adding new module
Create new directory
```console
$ mkdir minipupper-dev/modules/MyModule
$ touch minipupper-dev/modules/MyModule/interface.py
```
Open file in your editor and copy base module contonets to new file:
```python
from controller.module import BaseModule

# The class name must match script 
# Interface Class for interface.py 
# Controller Class for controller.py
class Interface(BaseModule):
    
    def __init__(self, args, shmem, in_list, out_list):
        super().__init__(args, shmem, in_list, out_list)
        # init only varibles here, no threads or process

    # no need to copy if not using
    def on_start(self):
      # your code here
      # can start threads or process here
      pass

    # no need to copy if not using
    def on_tick(self):
      # your code here
      # will be called by default every 16ms
      # to change default global tick edit contorller/module.py self.T_DELTA
      print(self)
    
    # no need to copy if not using
    def on_stop(self):
      # your cleanup code here
      pass
```
Replace "BaseModule" in Config.py for controller or interfaces section respectivelly.  
**Do not change speaker name**
```python
...
  "speaker": {
      "default": {
          # Module Folder Name
          "ModuleName": "MyModule",
          # Values here will be initialized durring __init__,
          # "Attributes": {"test": 1}, will be in module class self.test
          "Attributes": {},
          # not implemented            
          "AutoImport": True,
          # experimental, will be removed most likelly
          "AsyncInit": False,
          # 0 is main process, 1 is thread, 2 is subprocess
          "RunType": 99,
          # Order of when tick is called, cannot be same as other module, must be positive value between 0-99
          "RunPriority": 1,
          # Input shared memory that is defined in structures.py
          "InputMem": [],
          # Output shared memory that is defined in structures.py
          "OutputMem": [],
          }
      },
...
```
Test module only
```console
$ minipupper-dev/pupperctl.py --sound-only
```
### Shared Memmory IO
Controller is using synchronized arrays for shared memory structures supporting values and/or numpy arrays, memory structures are defined in [structures.py](modules/structures.py). Memory structures must be added to module config in InputMem/OutputMem respectivelly before they can be accessed from module.  

Intialized default values and read value every tick
```python
...
  def on_start(self):
    self.shm_write("SensorsIO", None, (0, 0, 0, 0, 0, 0, 0, 0, 0))

  def on_tick(self):
    enabled = self.shm_read("SensorsIO", "enable")
    print(enabled)
...
```

Write new value every tick
```python
...
  def on_tick(self):
    self.shm_write("SensorsIO", "enable", True)
...
```

Initialized and Write to numpy array every tick
```python
...
  def on_start(self):
    joint_angles = self.shm_numpy_out("ActuatorsIO").joint_angles
    self.shmout_joint_angles = np.frombuffer(joint_angles, dtype=np.float64 ).reshape(3, 4)

  def on_tick(self):
      joint_angles = np.random.rand(3,4)
      self.shmout_joint_angles[:] = joint_angles
...
```

Read numpy array every tick
```python
...
  def on_tick(self):
    _joint_angles = self.shm_read("ActuatorsIO", "joint_angles")
    joint_angles = np.array(_joint_angles[:]).reshape(3, 4)
    print(joint_angles)
...
```

## Licensing Issue
While most source code (not created by me) is licensed under MIT, current situation with licensing is not clear to say the least. 
Until licenses situation is not cleared up, seems the correct action is not attach any licenses to this repository.
Additionally docs and media files are not under Creative Commons Licenses.

### GPL source code in this repository
[EEPROM](drivers/EEPROM/)

[FuelGauge](drivers/FuelGauge)

### Unlisensed (eg. copyrighted by authors)
[PS4Joystick](modules/PS4Joystick)

[Original StandofrdRobiticsClub PS4Joystick Repository](https://github.com/stanfordroboticsclub/PS4Joystick)

### Not clear if this code is under MIT and if it is writen by MangDang Technology
[LCD](drivers/LCD)


**Before making any pull requests please connect me on discord.**

 <!-- Most likely some parts of python code will be rewriten in C -->