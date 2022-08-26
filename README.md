# MINIPUPPER-DEV

This is unofficial and early work in progress to (re)organize and "refactor" [MangDang's QuadrupedRobot](https://github.com/mangdangroboticsclub/QuadrupedRobot.git) repository.

The branch is not even version v0, there still much work to be done.

## Known Limitations
- Modules running as threads or in main will not properlly shotdown
- Deamon when started might fail to stop existing process(es)
- Incomplete implemenation of Config.py and args parser
- Joystick and Keyboard input is not well tested
- Kinematics modules might have bugs, specifically related to time delta
- Joystick at random times will fail to connect first time (driver issue, hard to isolate)
- When debuging, vscode will not start ssh with x forwarding, on debug stop pupperctl does not exit cleanly
- Calibration UI is not implemented 

## Notible changes from original code base
  - All services except rc.local are removed, rc.local is staged to be replaced with udev rules.
  - Code is organized into modules that are futher broken down into controllers and interfaces
  - Pupperctl application can be started from any where with modules arguments
  - Each module can be run as subprocess, thread, or be executed in main process
  - Display and Servos are only enabled when pupperctl is running
  - Python pip packages are installed and run as non-root user sudo is not required when starting pupperctl.py
  - UDPComms is completelly removed
  - Drivers installion scripts are removed and moved to makefiles
  - No need to connect network cable or monitor and keyboard/mouse to minipupper's RPi
  - Default Ubuntu image boot drive should be edited before first time boot to setup network and hardware
  - To save some RAM snap is completelly removed by defualt (it is optional)
  - EEPROM backup and restore script using rsync
  - TigerVNC Xfce4 remote desktop, as optinal install requeires TigerVNC Xfce4

### Getting started
```console
ubuntu@minipupper~$ git clone https://github.com/bitula/minipupper-dev
```
```console
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

Starting without display and no hardware (custom board), the board will be disabled including PWM's
```console
ubuntu@minipupper~$: minipupper-dev/pupperctl.py --joystick --no-display --no-hardware
interfaces default actuators
 shared memory HardwareIO intialized
 shared memory ActuatorsIO intialized
controllers default actuators
 shared memory SensorsIO intialized
interfaces default speaker
controllers default speaker
interfaces default joystick
 int:def:actuators:MiniPupperLegs initilized
 con:def:actuators:Kinematics initilized
 int:def:speaker:BaseModule initilized
 con:def:speaker:BaseModule initilized
 int:def:joystick:PS4Joystick initilized
 controller started with PID(s): 17680
 int:def:speaker:BaseModule subprocess starting
 int:def:actuators:MiniPupperLegs subprocess starting
 int:def:joystick:PS4Joystick subprocess starting
 con:def:speaker:BaseModule subprocess starting
 con:def:actuators:Kinematics subprocess starting
[info][controller 1] Created devices /dev/input/js0 (joystick) /dev/input/event2 (evdev) 
[info][bluetooth] Scanning for devices
```

### Adding new module
1. Create new directory in ~/minipupper-dev/modules
2. Create new interface.py or controller.py file
3. Copy base module contonets to new file:
```python
from controller.module import BaseModule

# must mach file name Interface for interface.py
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
      # to change default tick edit module.py self.T_DELTA
      print(self) # example
    
    # no need to copy if not using
    def on_stop(self):
      # your cleanup code here
      pass
```
4. Replace "BaseModule" in Config.py for controller or interfaces section respectivelly,   
**Do not change speaker name**
```python
...
  "speaker": {
      "default": {
          "ModuleName": "BaseModule",
          "Attributes": {},
          "AutoImport": True,
          "AsyncInit": False,
          "RunType": 1,
          "RunPriority": 1,
          "InputMem": [],
          "OutputMem": [],
          }
      },
...
```
5. Test module only
```console
minipupper-dev/pupperctl.py --sound-only
```
7. See other modules implementations and launch.json config for debuging

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