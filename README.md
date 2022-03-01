
![License: MIT](https://img.shields.io/github/license/intelligent-environments-lab/airthings-waveplus-beacon?style=plastic)
![GitHub top language](https://img.shields.io/github/languages/top/intelligent-environments-lab/airthings-waveplus-beacon?style=plastic)

# Airthings Wave Plus Beacon


### Project Description
This inspiration for this project was to help remove the need for an AirThings Hub to collect data from AirThings WavePlus sensors. Instead, we use a Raspberry Pi (RPi) that periodically pings a specified, nearby AirThings device via bluetooth to gather and store data. We can easily access the RPi for data at any point so long as it is connected to WiFi. 

_This repository was forked from https://github.com/kogant/waveplus-reader_

Data are collected via a Python script [read_data.py](https://github.com/intelligent-environments-lab/airthings-waveplus-beacon/blob/master/src/read_data.py) that, once executed, runs indefinitely collecting data at 1-minute intervals and appending these data to a locally-stored daily CSV file within in the ```/home/pi/DATA``` directory. 

### Necessary Libraries
The libraries needed to run this project as intended are listed in the [install.sh](https://github.com/intelligent-environments-lab/airthings-waveplus-beacon/blob/master/install.sh) script, but we highlight some of the more important ones below:
* python 3.7+
* pip3
* bluepy
* NumPy and Pandas

### Setup

1. On the RPi, install git and clone this repo

```bash
sudo apt install git
```

```bash
git clone https://github.com/intelligent-environments-lab/airthings-waveplus-beacon.git
```
2. Run the install shell script with

```bash
sh install.sh
```

3. The ```read_data.py``` script is meant to run indefinitely in the background so we enable it on boot with a service file. First, edit the file ```read_data.service``` by including the 11-digit serial number of the AirThings Device at the end of the ```ExecStart``` line. Then, to create and enable the service, run:

```bash
sh services/services.sh
```

4. Reboot the device and check that data has been added to the ```/home/pi/DATA/``` directory (you might need to create this location with ```mkdir DATA```). If no data are available, use ```sudo journalctl -u read_data.service``` to check and debug the errors you see. 

5. You can also test the script by running the Python script directly from the command line:

```bash
sudo python3 /home/pi/airthings-waveplus-beacon/src/read_data.py <airthings_serial_number>
```
