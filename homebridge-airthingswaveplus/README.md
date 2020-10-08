# Install doc homebridge #
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

# homebridge module installation
copy the homebridge-airthingswaveplus folder to /usr/lib/node_modules/homebridge-airthingswaveplus/


# open website in browser
http://ip:8581
# login with admin/admin


# homebridge config (add in webpage)

```js
"accessories": [
        {
            "accessory": "Airthings",
            "name": "Airthings Wave Plus",
            "name_temperature": "Temperature",
            "name_humidity": "Humidity",
            "name_radonst": "Radon Short Term",
            "name_pressure": "Air Pressure",
            "name_radon_st": "Radon Short Term",
            "name_radon_lt": "Radon Long Term",
            "name_CO2_lvl": "CO2",
            "name_VOC_lvl": "TVOC",
            "serialnumber": "INSERTSERIALNUMBER",
            "carbonDioxideThreshold": 800,
            "carbonDioxideThresholdOff ": 500,
            "refresh": 120,
            "logpath": "/tmp/airthingswave.status.json"
        }
    ],
 ```
