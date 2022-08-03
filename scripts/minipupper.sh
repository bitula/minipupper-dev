######  INSTALL  ######

printf '%s\n' 'Installing MiniPupper Drivers'

### Install python dependecies
pip3 install Pillow RPi.GPIO numpy spidev transforms3d

## Install boot service
sudo cp $PWD/init/rc.local /etc/
sudo cp $PWD/init/rc-local.service /lib/systemd/system/

sudo sed -i "s|REPODIR|$PWD|" /etc/rc.local
sudo sed -i "s/3-00500/3-00501/" /etc/rc.local

## Install controller board drivers and services

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

printf '%s\n' 'Batter Monitor Installed'

sudo systemctl enable  battery_monitor.service

sudo systemctl enable rc-local

printf '%s\n' 'MiniPupper Drivers Installation Completed'

### Keyboard Mouse Input 

pip install pynput
# Required for x forwarding, so far worked better the any other terminal emulator
sudo apt install urxvt
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