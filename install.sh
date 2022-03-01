
#!/bin/bash

# Update package list
sudo apt-get update
sudo apt-get -y upgrade

# Additional apt packages
sudo apt-get install python3 -y
sudo apt-get install python3-pip -y
sudo apt-get install python3-venv -y
sudo apt-get install -y i2c-tools

# Bluetooth
sudo pip3 install bluepy
chmod +x /usr/local/lib/python3.7/dist-packages/bluepy/bluepy-helper

# Reboot - might need this in case we encounter any issues
#sudo /bin/bash -c 'echo "59 23 * * * root sh /home/pi/bevo_iaq/reboot.sh" >> /etc/crontab'

# VPN
sudo apt-get install apt-transport-https
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.gpg | sudo apt-key add -
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt-get update
sudo apt-get install tailscale

# Set up locale, timezone, language
sudo timedatectl set-timezone US/Central

# Python Packages for Script
sudo apt-get install -y libatlas-base-dev #for numpy
sudo pip3 install pandas
sudo pip3 install numpy
