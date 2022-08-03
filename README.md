# MINIPUPPER-DEV

This is unofficial and very early work in progress to (re)organize and "refactor" [MangDang's QuadrupedRobot](https://github.com/mangdangroboticsclub/QuadrupedRobot.git) repository, in large part insipired by [minipupper_base](https://github.com/hdumcke/minipupper_base.git) repository created by [@hdumcke](https://github.com/hdumcke).

## Some notible changes:
  - No need to connect network cable or monitor and keyboard/mouse to minipupper's RPi
  - UDPComms is completelly removed
  - All services except battery and rc.local are removed
  - Drivers installion scripts are removed and moved to makefiles
  - Code is reorganized into folders in a more self-discriptive way
  - Python pip packages are installed and run as non-root user
  - To save some RAM snap is completelly removed by defualt (it is optional)
  - Added TigerVNC Xfce4 remote desktop, as optinal install
  - Default Ubuntu image boot drive is needs to be edited before first time boot
  - Python imports almost every where are edited, py scripts will work under any user from any folder location.
  - For now run_robot.py needs to be started manually via ssh or vnc (seems like joystick works better now)

## Licensing Issue
While most source code is licensed under MIT, current situation with licensing is not clear to say the least. 
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

# Instalation Guide

Where console command start with [ ```$ ...``` ] this commands are run on your workstion, commands that are executed on minipuppers RPi start with [ ```ubuntu@minipupper:~$ ...``` ]

While upgraded ubuntu image works just fine, current installation guide does not use it, because minipuer upgrade script is not implemented.

This guide is intended to be run from any Linux distribution, except vnc viewer, most if not all commands should be preinstalled by defualt on your workstation.

## Prepare Ubuntu 22.04 Rasberry Pi Server Image

Downalod image
```console
$ wget https://cdimage.ubuntu.com/releases/22.04/release/ubuntu-22.04-preinstalled-server-arm64+raspi.img.xz
```
Verify image
```console
$ echo "9cd6b5e6b4e4a7453cfde276927efe20380ab9ec0377318d5ce0bc8c8a56993b *ubuntu-22.04-preinstalled-server-arm64+raspi.img.xz" | shasum -a 256 --check
```

Unzipe image
```console
$ unxz ubuntu-22.04-preinstalled-server-arm64+raspi.img.xz
```
<!-- TODO add download script with gpg key verification  -->

## Copy image to microSD card
Find microSD card device path (at all times check and double check)
```console
$ sudo fdisk -l
```
    ATTENTION!  ATTENTION!  ATTENTION! 
  
    Executing dd command below with a wrong device path (eg. /dev/sdX) argument, can and 
    probably will break your system, and result in losing all data on harddrive(s).

Replace X in /dev/sdX with CORRECT latter and copy image to microSD card, ALL data on the SD card will be EARSED.
```console
$ sudo dd if=ubuntu-22.04-preinstalled-server-arm64+raspi.img of=/dev/sdX bs=4M status=progress; sync;
```
## Prepare image boot config
Make sure nothing is mounted in the /mnt path
```consle
$ sudo umount /mnt
```

Create directory and mount /dev/sdX1, replace X with correct latter, number "1" should be after latter

```console
$ sudo mkdir /mnt/minipupper
$ sudo mount /dev/sdX1 /mnt/minipupper

Clone repository and copy config.txt to minipupper's boot drive
```console
$ git clone https://github.com/bitula/minipupper-dev
$ sudo cp ~/minipupper-dev/init/config.txt /mnt/minipupper/
```

Edit network-config
```console
$ sudo nano /mnt/minipupper/network-config
```

Uncomment wifi lines like in example below, edit to your wifi name (SSID) "myhomewifi" and S3kr1t to you password.
Depending on your router configuration, if minipupper is powerd off for long time DHCP ip address might be changed, it might be better to setup static ip here, and skip "Prepare workstation to find minipupper ip address" step.

```console
$ cat /mnt/minipupper/network-config
...
wifis:
  wlan0:
    dhcp4: true
    optional: true
    access-points:
      myhomewifi:
        password: "S3kr1t"
...
```

Edit user-data

```console
$ sudo nano /mnt/minipupper/user-data
```
Set exprire to false, and change hostname to minipupper
```console
$ cat /mnt/minipupper/user-data
...
chpasswd:
  expire: false
  list:
  - ubuntu:ubuntu
  
hostname: minipupper
...
```
[OPTIONAL] Backup config files, **do not copy them into cloned repository**
```console
$ mkdir PupperBackupFolderName
$ cp /mnt/minipupper/user-data ~/PupperBackupFolderName/user-data.bkp0
$ cp /mnt/minipupper/network-config ~/PupperBackupFolderName/network-config.bkp0
```
Unmount microSD
```console
$ sudo umount /mnt/minipupper/
```
**Do not boot RPi yet.**



## Prepare workstation to find minipupper ip address

Before powering up minipupper, assuming; workstation is conneted to the same network and it is on same subnet:

Start tcpdump to listen for DHCP request (skip tcpdump step if sure router will detect Rasberry Pi, openwrt does)
```console
$ sudo tcpdump -i [YourIntefaceName] port 67 or port 68 -e -n
```
If you don't know what interface workstaion is using, first run command below and then command above, usually it is 192.168.1.0 or 192.168.0.0, and not 127.0.0.1.
```console
$ ip a
2: [YourIntefaceName]: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 
...
    inet X.X.X.X/24 brd X.X.X.X scope global [YourIntefaceName]
...
```

    Insert microSD into minipupper's RPi and power up 

The tcpdump command after few seconds should show DHCP requests from RPi with RPi mac address
```console
sudo tcpdump -i enp10s0 port 67 or port 68 -e -n
...
12:01:01.160898 FF:FF:FF:FF:FF:FF > ff:ff:ff:ff:ff:ff, ethertype IPv4 (0x0800), length 336: 0.0.0.0.68 > 255.255.255.255.67: BOOTP/DHCP, Request from FF:FF:FF:FF:FF:FF, length 294
12:01:01.160898 FF:FF:FF:FF:FF:FF > ff:ff:ff:ff:ff:ff, ethertype IPv4 (0x0800), length 348: 0.0.0.0.68 > 255.255.255.255.67: BOOTP/DHCP, Request from FF:FF:FF:FF:FF:FF, length 306
...
```
Stop tcpdump (Ctrl+C) and scan network, replace with correct subnet (usually 192.168.1.0 or 192.168.0.0), last digite must be 0

```console
$ sudo nmap -sP X.X.X.0/24
... 
map scan report for ubuntu (X.X.X.X)
Host is up (0.062s latency).
MAC Address: FF:FF:FF:FF:FF:FF (...)
...
```
If hostname ubunutu is not display use mac address (FF:FF:FF:FF:FF:FF) to identify minipupper ip address

If this did not work (might be because of wifi/wired network setup on router) then easist way would be to just mount microSD card on workstation again and set static ip, instead of DHCP config.


## Set up passwordless access to minipupper 

Generate ssh key
```console
$ ssh-keygen -t rsa -b 4096 -f ~/.ssh/minipupper
```

replace X.X.X.X with correct ip and copy ssh key to minipupper, default password is: ubuntu
```console
$ cat ~/.ssh/minipupper.pub | ssh ubuntu@X.X.X.X 'dd of=.ssh/authorized_keys oflag=append conv=notrunc'
```

Edit ssh configuration or if does not exist create one git rebase -i --root release-test
$ rsync -r ~/minipupper-dev/ minipupper:~/minipupper
``` 
SSH into minipupper
```console
$ ssh minipupper
```
To avoid any interupts in case workstation disconnects use tmux to run critical updates/installations
```console
ubuntu@minipupper:~$ tmux
ubuntu@minipupper:~$ cd minipupper
```
<!-- TODO add option to start tmux by defualt:
 https://stackoverflow.com/questions/27613209/how-to-automatically-start-tmux-on-ssh-session -->

[OPTIONAL] Install vnc (remote desktop access to minipupper), uncomment ./scripts/xfcevnc.sh in install.sh
  
```console
ubuntu@minipupper:~/minipupper$ nano install.sh
ubuntu@minipupper:~/minipupper$ cat ~/minipupper-dev/install.sh
...
### INSTALL XFC4 & VNCSERVER ### 
./scripts/xfcevnc.sh
...
```

[OPTIONAL] Do not purge snap, comment out snap removal
```console
ubuntu@minipupper:~/minipupper$ nano install.sh 
ubuntu@minipupper:~/minipupper$ cat install.sh
...
# ##### PURGE SNAP ######
# sudo snap remove lxd
# sudo systemctl stop snapd
# sudo apt remove --purge --assume-yes snapd gnome-software-plugin-snap
# rm -rf ~/snap/
# sudo rm -rf /var/cache/snapd/
...
```

Start insall script, script will reboot RPi when finished
```console
ubuntu@minipupper~/minipupper$ ./install.sh
```
## Test joystick
When minipupper is booting, it will make squeaking noise; ~/minipupper-dev/assets/battery_sounds/power_on.mp3
```consle
$ ssh minipupper
```
Start calibration cli (see guide below for gui tool)
```console
ubuntu@minipupper:~$ cd minipupper/ 
ubuntu@minipupper:~/minipupper$ python3 pupperctl/calibration/calibrate_servos.py  
```

Start joystick script
```console
ubuntu@minipupper:~$ cd minipupper
ubuntu@minipupper:~/minipupper$ python3 pupperctl/joystick/run_robot.py
```

Once run_robot.py is started screen should turn on.

To connect to joystick hold home button until light starts blinking and after some time light turns green.

If light on joystick turned off, Press and Hold button again (it is not clear why sometimes joystick does not connect)

Once joystick is connected, press L1 to arm minipupper.

<!-- TODO debug bluetooth guide -->

## [OPTIONAL] Setup vscode remote access on workstation
<!-- Improve this guide -->
Setup vscode development on minipupper 

    On Workstiaon: 
    1. Install vscode
    2. Install vscode Remote SSH extension
    3. Start vscode
    4. Navigate to remote Remote Explorer
    5. Connect to minipupper
    6. Open PathToRepo[ TODO ]

## Setup and connect to pupper via VNC, if you have vnc server installed
To connect to minipupper to vnc server via ssh tunnel
```Console
$ ssh minipupper -L 5901:127.0.0.1:5901
```
Start vncserver on minipupper
```console
ubuntu@minipupper:~$ tigervncserver -SecurityTypes None --I-KNOW-THIS-IS-INSECURE -localhost no :1
```

Kill vnc server, when you not using it
```console
ubuntu@minipupper:~$ tigervncserver -kill :1
Killing Xtigervnc process ID XXXX ... success!
```

In workstation second terminal
```console
$ sudo apt-get update -y
$ sudo apt-get install -y tigervnc-viewer
$ vncviewer 127.0.0.1:5901
```

Start terminal in vncviewer window and run callibration tool:
```console
ubuntu@minipupper:~$ cd minipupper/
ubuntu@minipupper:~/minipupper$ python3 pupperctl/calibration/calibrate_tool.py
```

In case you did not installed vnc server durring initial installtion, run xfcevnc installation script
```console
ubuntu@minipupper:~$ cd minipupper
ubuntu@minipupper:~/minipupper$ /scripts/xfcevnc.sh
```

<!-- TODO add windows/mac guide -->

## Finally backup MicroSD

Shutdown minipupper
```console
ubuntu@pupper:~$ shutdown now
```

Backup  micro SD to workstaion
```console
$ sudo fdisk -l
$ sudo dd if=/dev/sdX of=minipupper-bk0.img bs=4M conv=sparse status=progress; sync;
```

Instead of backing up MicroSD you can simply sync changes back to workstation by using rsync with reverse source and destation (minipupper must be pwered on)
```console
$ rsync -r minipupper:~/minipupper/ ~/minipupper-dev
```
<!-- TODO create rsync script to igoner repo and temp files -->

## The Approximated Future
 - Automation of workstation first time setup
 - Custom Ubuntu Image
 - Configs files for Minipupper parameters 
 - Keyboard/mouse control
 - Website Interface for control and callibration
 - Cross platform Interface (Windows, IOS, Android)
 - Sensors such as lidar, camera, and accelerometer sensor 
 - ROS2 with Gazebo Simulator
 - Docs Website

 <!-- Most likely some parts of python code will be rewriten in C -->