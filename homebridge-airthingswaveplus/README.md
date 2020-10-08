## Install doc homebridge ##
ض# Take 2
#install raspian latest version using raspberry pi image writer.
before mounting it on the raspberry pi, create a empty file called "ssh" in the root folder of the card.
insert ethernet cable
power on
ssh to device ip
user: pi
password: raspberry

#change password
passwd
# setup wifi (if needed)
sudo raspi-config
# upgrade firmware
sudo rpi-update
# reboot & disconnect ethernet cable(if needed)
sudo reboot
# upgrade OS
sudo apt-get update && sudo apt-get upgrade -y
# setup repo
curl -sL https://deb.nodesource.com/setup_12.x | sudo bash -

# install Node.js
sudo apt-get install -y nodejs gcc g++ make python

# test node is working
node -v
# install homebridge
sudo npm install -g --unsafe-perm homebridge homebridge-config-ui-x
# set the service to start at boot
sudo hb-service install --user homebridge

# open website in browser
http://ip:8581
# login with admin/admin
