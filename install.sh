#!/bin/bash

###### BASE ISNTALL ######

# TODO add log to file here 
# install.sh 2>&1 | tee -a my_log

# TODO add getopts, and install stage checkpoint

## Prevent starting unattended-upgrade during script execution
for TARGET_FILE in $(grep -ril "Update-Package-Lists" /etc/apt/apt.conf.d/); do
     echo Rewriting $TARGET_FILE
     sudo sed -i -e 's/Update-Package-Lists "1"/Update-Package-Lists "0"/g' -e 's/Unattended-Upgrade "1"/Unattended-Upgrade "0"/g' $TARGET_FILE
done

### Update && Upgrade
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
sudo sed -i "s/# deb-src/deb-src/g" /etc/apt/sources.list

###### PURGE SNAP ######
sudo snap remove lxd
sudo systemctl stop snapd
sudo apt remove --purge --assume-yes snapd gnome-software-plugin-snap
rm -rf ~/snap/
sudo rm -rf /var/cache/snapd/

sudo apt update

###  Configure minipupper audio
sudo apt install -y mpg321
sudo sed -i "s/pulse/alsa/" /etc/libao.conf
sudo sed -i "s/cards.pcm.front/cards.pcm.default/" /usr/share/alsa/alsa.conf

### Install dependecies
sudo apt install -y mc i2c-tools dpkg-dev python-is-python3 python3-tk python3-dev


### Install pip
wget https://bootstrap.pypa.io/get-pip.py -P /tmp
python3 /tmp/get-pip.py

### while .profile has path it does fails to reloaded
### echo "export PATH=\"/home/$USER/.local/bin:\$PATH\"" >> ~/.bashrc && . ~/.bashrc
. ~/.profile


### INSTALL XFC4 & VNCSERVER ### 
# TODO should be specified with getops
# ./scripts/xfcevnc.sh


### INSTALL MINIPUPPER ###
# TODO should be specified with getops
./scripts/minipupper.sh


### POST INSTALL ###

## Enable packge updates
sudo sed -i -e 's/Update-Package-Lists "0"/Update-Package-Lists "1"/g' /etc/apt/apt.conf.d/20auto-upgrades

### Why this is removed ?
# sudo apt-get remove -y ubuntu-release-upgrader-core

# Cleanup
sudo apt -y autoremove

printf '%s\n' 'Installation is completed, rebooting minipupper'

shutdown -r 1


############################
###### UPDATE UBUNTU #######
# TODO

# sudo apt update && sudo apt -y upgrade
# if kernel is updated:
     # sudo reboot

# reinstall minipupper
# ./scripts/minipupper.sh --update
     # issue with reboot is that makefiles read current 
     # kernel version and not updated one that is pending reboot
     
     # backup calibration data
     # reinstall EEPROM, FuelGauge
     # restore calibration data

# sudo reboot
