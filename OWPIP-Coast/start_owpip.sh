#! /bin/bash

# Launches the Label-Viewer Python program on startup
# Usage: place in /home/pi and chmod 744
# in /home/pi/.config/lxsession/LDXE-pi/autostart add:
# @/home/pi/viewer_startup.sh

echo "###############" >> /var/log/owpip.log
date >> /var/log/owpip.log
cd /home/pi/Desktop/OWPIP-Coast
python owpip-coast.py >> /var/log/owpip.log
