### potentiall missing package
sudo apt install -y xfwm4 at-spi2-core
sudo apt install -y dbus-x11 x11-xfs-utils x11-utils

### Install Xfce Desktop
### TODO sudo apt-get install -y --no-install-recommends xfce4
sudo apt install -y xfce4 xfce4-goodies # something like 50% of packages are not needed should be build with --no-install-reco$

### TigerVNC Server
sudo apt install -y tigervnc-standalone-server tigervnc-xorg-extension

### Create xstartup script
mkdir -p ~/.vnc

# TODO fix issue with premissions 
cat > ~/.vnc/xstartup << OUTER
#!/bin/sh
test x"\$SHELL" = x"" && SHELL=/bin/bash
test x"\$1"     = x"" && set -- default

unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS

[ -x /etc/vnc/xstartup ] && exec /etc/vnc/xstartup
[ -r $\HOME/.Xresources ] && xrdb \$HOME/.Xresources

#xhost +localhost
#xsetroot -solid grey

vncconfig -iconic &
x-window-manager &

"\$SHELL" -l << EOF
export XDG_SESSION_TYPE=x11
#export GNOME_SHELL_SESSION_MODE=ubuntu
dbus-launch --exit-with-session xfce4-session #--session=ubuntu
EOF
vncserver -kill \$DISPLAY
# TODO fix logout 
OUTER

sudo chmod +x ~/.vnc/xstartup

