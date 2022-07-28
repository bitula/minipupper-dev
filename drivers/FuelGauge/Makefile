#
# The makefile for max17205 driver build
#

MK_PATH:=$(dir $(realpath $(lastword $(MAKEFILE_LIST))))
MK_PARENT:=$(realpath $(MK_PATH)../..)

obj-m += max1720x_battery.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

install:
	sudo cp max1720x_battery.ko /lib/modules/`uname -r`/kernel/drivers/power/supply/
	sudo depmod -a
	
	dtc i2c4.dts > i2c4.dtbo
	sudo cp i2c4.dtbo /boot/firmware/overlays/

	sudo cp battery_monitor /usr/bin/
	sudo sed -i "s|BASEDIR|$(MK_PARENT)|" /usr/bin/battery_monitor
	sudo cp battery_monitor.service /lib/systemd/system/