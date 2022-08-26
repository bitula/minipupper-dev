######  INSTALL  ######

printf '%s\n' 'Installing MiniPupper Drivers'

### Install python dependecies
pip3 install Pillow RPi.GPIO numpy spidev transforms3d


## Install controller board drivers and udev rules
printf '%s\n' 'Installing EEPROM Driver'

cd $PWD/drivers/EEPROM/

make clean
make
make install

printf '%s\n' 'EEPROM Installed'

cd ../..

printf '%s\n' 'Installing Batter Monitor Driver and Service'

cd $PWD/drivers/FuelGauge/
make clean
make
make install

printf '%s\n' 'MiniPupper Drivers Installation Completed'

printf '%s\n' 'Installling UDEV Rules'

sudo cat > /tmp/99-minipupper.rules << EOF
KERNEL=="pwmchip0", SUBSYSTEM=="pwm", ACTION=="add", RUN+="pwm-minipupper.sh"
### might not work on all rpi's, because of label attribute, without label script will exec twice.
KERNELS=="gpiochip0", SUBSYSTEM=="gpio", ACTION=="add", ATTR{label}=="pinctrl-bcm2711", RUN+="gpio-minipupper.sh"
KERNEL=="3-00501", SUBSYSTEM=="nvmem", ACTION=="add", PROGRAM="/bin/sh -c 'chmod 666 /sys/bus/nvmem/devices/3-00501/nvmem'"
EOF

sudo cp /tmp/99-minipupper.rules /etc/udev/rules.d/

sudo cat > /tmp/pwm-minipupper.sh << "EOF"
#!/bin/bash

for i in $(seq 4 15)
    do
        echo $i > /sys/class/pwm/pwmchip0/export
        echo  4000000 > /sys/class/pwm/pwmchip0/pwm$i/period
        chmod 666 /sys/class/pwm/pwmchip0/pwm$i/duty_cycle
        chmod 666 /sys/class/pwm/pwmchip0/pwm$i/enable
    done
EOF

sudo chmod +x /tmp/pwm-minipupper.sh
sudo cp /tmp/pwm-minipupper.sh /lib/udev

sudo cat > /tmp/gpio-minipupper.sh << EOF
#!/bin/bash

# Board power
echo 21 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio21/direction
chmod 666 /sys/class/gpio/gpio21/value

echo 25 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio25/direction
chmod 666 /sys/class/gpio/gpio25/value

# LCD power
echo 26 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio26/direction
chmod 666 /sys/class/gpio/gpio26/value
EOF

sudo chmod +x /tmp/gpio-minipupper.sh
sudo cp /tmp/gpio-minipupper.sh /lib/udev

printf '%s\n' 'UDEV Rules Installed'

### Keyboard Mouse Input 
pip install pynput

# Required for x forwarding, so far worked better the any other terminal emulator
sudo apt install rxvt-unicode
# TODO add config for urxvt 

printf '%s\n' 'Installing Joystic'

pip3 install ds4drv # probably should just clone ds4drv

sudo cat > /tmp/50-ds4drv.rules << EOF
KERNEL=="uinput", MODE="0666"
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="05c4", MODE="0666"
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", KERNELS=="0005:054C:05C4.*", MODE="0666"
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="09cc", MODE="0666"
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", KERNELS=="0005:054C:09CC.*", MODE="0666"
EOF

sudo cp /tmp/50-ds4drv.rules /etc/udev/rules.d/

printf '%s\n' 'Joystick installed'
