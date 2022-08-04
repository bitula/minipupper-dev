#!/bin/bash

DIR_PATH=$HOME
BACKUP_PATH=$DIR_PATH/minipupper-dev/eeprom

if [[ "$HOSTNAME" == "minipupper" ]]; then
    echo "Error: this script should be executed on remote machine with ssh access to minipupper"
    exit 1
fi

if [[ "$1" == *"--restore"* ]]; then

    if [[ "$2" == *"/"* ]];then
        echo "Error: must specify filename only, without dir path(s)"
        exit 1
    fi

    if [ "$PWD" != "$BACKUP_PATH" ]; then
        cd $BACKUP_PATH
    fi
    
    if [ ! -f "$2" ]; then
        echo "Error: backup file does not exist"
        exit
    fi

    echo "Copying $2 to minipupper"
    echo
    rsync $2 minipupper:/tmp/

    echo "Restoring $2 on minipupper"
    echo
    ssh minipupper "dd if=/tmp/$2 of=/sys/bus/nvmem/devices/3-00501/nvmem; sync;"
    exit
fi

TIMESTAMP=`date "+%Y%m%d-%H%M%S"`
BACKUP_NAME="$TIMESTAMP.eeprom"

echo "Creating $BACKUP_NAME backup"
echo
ssh minipupper "dd if=/sys/bus/nvmem/devices/3-00501/nvmem of=/tmp/$BACKUP_NAME; sync;"
echo

create_dir () {
  echo "Creating Directory"
  if [ ! -d "$DIR_PATH/minipupper-dev" ]; then
    mkdir -p $BACKUP_PATH
  else
    mkdir $DIR_PATH/minipupper-dev/eeprom
  fi
}

if [ ! -d  $BACKUP_PATH ]; then
    echo "Directory $BACKUP_PATH does not exist!"
    while true; do
        read -p "Do you wish to create directory? " yn
        case $yn in
            [Yy]* ) create_dir; break;;
            [Nn]* ) echo "bye"; exit;;
            * ) echo "Please answer yes or no.";;
        esac
    done
fi

echo "Copying $BACKUP_NAME to $BACKUP_PATH/"
echo
rsync minipupper:/tmp/$BACKUP_NAME $BACKUP_PATH/