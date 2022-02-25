# MIT License
#
# Copyright (c) 2018 Airthings AS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://airthings.com

# ===============================
# Module import dependencies
# ===============================

from xml.dom.minidom import parseString
from bluepy.btle import UUID, Peripheral, Scanner, DefaultDelegate
import sys
import time
import struct
import os.path
import logging

from datetime import datetime
import pandas as pd
import numpy as np

# ====================================
# Utility functions
# ====================================

def parseSerialNumber(ManuDataHexStr):
    """
    Parses the serial number from a hex string
    """
    if (ManuDataHexStr == "None"):
        SN = "Unknown"
    else:
        ManuData = bytearray.fromhex(ManuDataHexStr)

        if (((ManuData[1] << 8) | ManuData[0]) == 0x0334):
            SN  =  ManuData[2]
            SN |= (ManuData[3] << 8)
            SN |= (ManuData[4] << 16)
            SN |= (ManuData[5] << 24)
        else:
            SN = "Unknown"
    return SN

def get_error_data():
    """
    Returns NaN data for each sensor
    """
    data = {
        "humidity": [np.nan],
        "radon_st_avg": [np.nan],
        "radon_lt_avg": [np.nan],
        "temperature": [np.nan],
        "pressure": [np.nan],
        "CO2_lvl": [np.nan],
        "VOC_lvl": [np.nan]
    }
    return data

# ===============================
# Class WavePlus
# ===============================

class WavePlus():
    def __init__(self, SerialNumber):
        self.periph        = None
        self.curr_val_char = None
        self.MacAddr       = None
        self.SN            = SerialNumber
        self.uuid          = UUID("b42e2a68-ade7-11e4-89d3-123b93f75cba")

    def connect(self):
        # Auto-discover device on first connection
        if (self.MacAddr is None):
            scanner     = Scanner().withDelegate(DefaultDelegate())
            searchCount = 0
            while self.MacAddr is None and searchCount < 50:
                devices      = scanner.scan(0.1) # 0.1 seconds scan period
                searchCount += 1
                for dev in devices:
                    ManuData = dev.getValueText(255)
                    if ManuData is not None:
                        SN = parseSerialNumber(ManuData)
                        if (SN == self.SN):
                            self.MacAddr = dev.addr # exits the while loop on next conditional check
                    else:
                        self.MacAddr = None
                    break # exit for loop
            
            if (self.MacAddr is None):
                raise NameError("Could not find device")
        
        # Connect to device
        if (self.periph is None):
            self.periph = Peripheral(self.MacAddr)
        if (self.curr_val_char is None):
            self.curr_val_char = self.periph.getCharacteristics(uuid=self.uuid)[0]
        
    def read(self):
        if (self.curr_val_char is None):
            raise NameError("Devices are not connected")          
        rawdata = self.curr_val_char.read()
        rawdata = struct.unpack('BBBBHHHHHHHH', rawdata)
        sensors = Sensors()
        sensors.set(rawdata)
        return sensors
    
    def disconnect(self):
        if self.periph is not None:
            self.periph.disconnect()
            self.periph = None
            self.curr_val_char = None

# ===================================
# Class Sensor and sensor definitions
# ===================================

NUMBER_OF_SENSORS               = 7
SENSOR_IDX_HUMIDITY             = 0
SENSOR_IDX_RADON_SHORT_TERM_AVG = 1
SENSOR_IDX_RADON_LONG_TERM_AVG  = 2
SENSOR_IDX_TEMPERATURE          = 3
SENSOR_IDX_REL_ATM_PRESSURE     = 4
SENSOR_IDX_CO2_LVL              = 5
SENSOR_IDX_VOC_LVL              = 6

class Sensors():
    def __init__(self):
        self.sensor_version = None
        self.sensor_data    = [None]*NUMBER_OF_SENSORS
        self.sensor_units   = ["%", "Bq/m3", "Bq/m3", "degC", "hPa", "ppm", "ppb"]
    
    def set(self, rawData):
        self.sensor_version = rawData[0]
        if (self.sensor_version == 1):
            self.sensor_data[SENSOR_IDX_HUMIDITY]             = rawData[1]/2.0
            self.sensor_data[SENSOR_IDX_RADON_SHORT_TERM_AVG] = self.conv2radon(rawData[4])
            self.sensor_data[SENSOR_IDX_RADON_LONG_TERM_AVG]  = self.conv2radon(rawData[5])
            self.sensor_data[SENSOR_IDX_TEMPERATURE]          = rawData[6]/100.0
            self.sensor_data[SENSOR_IDX_REL_ATM_PRESSURE]     = rawData[7]/50.0
            self.sensor_data[SENSOR_IDX_CO2_LVL]              = rawData[8]*1.0
            self.sensor_data[SENSOR_IDX_VOC_LVL]              = rawData[9]*1.0
        else:
            print("ERROR: Unknown sensor version.\n")
            print("GUIDE: Contact Airthings for support.\n")
            sys.exit(1) # keeping this error because it seems necessary
   
    def conv2radon(self, radon_raw):
        radon = "N/A" # Either invalid measurement, or not available
        if 0 <= radon_raw <= 16383:
            radon  = radon_raw
        return radon

    def getValue(self, sensor_index):
        return self.sensor_data[sensor_index]

    def getUnit(self, sensor_index):
        return self.sensor_units[sensor_index]
        
def main(SerialNumber):
    """
    Main function
    """
    log = setup_logger(logging.INFO)
    waveplus = WavePlus(SerialNumber)
    log.info("--------------------------------------------------------------------------------------")
    log.info("Created AirThings Object")
    log.info(f"Serial Number: {SerialNumber}")
    log.info("--------------------------------------------------------------------------------------")
    starttime = time.time()  # Used for preventing time drift
    while True:
        date = datetime.now()
        cylce_start_time = time.time()  # Used for evaluating scan cycle time performance
        try:
            #---- Connect ----#
            try:
                waveplus.connect()
                log.info("Connected to AirThings")
                log.info("--------------------------------------------------------------------------------------")
            except NameError as e:
                log.warning(e)
                # create temp file
                data = get_error_data()
                
            #---- Read ----#
            try:
                sensors = waveplus.read()

                humidity     = str(sensors.getValue(SENSOR_IDX_HUMIDITY))
                radon_st_avg = str(sensors.getValue(SENSOR_IDX_RADON_SHORT_TERM_AVG))
                radon_lt_avg = str(sensors.getValue(SENSOR_IDX_RADON_LONG_TERM_AVG))
                temperature  = str(sensors.getValue(SENSOR_IDX_TEMPERATURE))
                pressure     = str(sensors.getValue(SENSOR_IDX_REL_ATM_PRESSURE))
                CO2_lvl      = str(sensors.getValue(SENSOR_IDX_CO2_LVL))
                VOC_lvl      = str(sensors.getValue(SENSOR_IDX_VOC_LVL))

                data = {
                    "timestamp": [date.strftime('%Y-%m-%d %H:%M:%S')],
                    "rh": [humidity],
                    "radon_acute": [radon_st_avg],
                    "radon_chronic": [radon_lt_avg],
                    "temperature": [temperature],
                    "pressure": [pressure],
                    "co2": [CO2_lvl],
                    "voc": [VOC_lvl]
                    }
            except NameError as e:
                log.warning(e)
                # create temp file
                data = get_error_data()

            # convert to dataframe and output to log
            df = pd.DataFrame(data).set_index("timestamp")
            log.info(df)
            log.info("--------------------------------------------------------------------------------------")
            
            # Write data to csv file
            filename = f'/home/pi/DATA/{SerialNumber}-{date.strftime("%Y-%m-%d")}.csv'
            try:
                if os.path.isfile(filename):
                    df.to_csv(filename, mode="a", header=False)
                    log.info(f"Data appended to {filename}")
                else:
                    # create file locally
                    df.to_csv(filename)
                    log.info(f"Data written to {filename}")
            except Exception as e:
                log.warning(e)

        finally:
            waveplus.disconnect()

        # Report cycle time for performance evaluation by user
        elapsed_time = time.time() - cylce_start_time
        log.info(f"Cycle Time:\t{round(elapsed_time,2)} seconds")

        # Make sure that interval between scans is exactly 60 secondss
        log.info(f"Sleeping:\t{round(60.0 - ((time.time() - starttime) % 60.0),2)} seconds")
        log.info("--------------------------------------------------------------------------------------\n")
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

def setup_logger(level=logging.WARNING):
    """
    logging setup for standard and file output
    """
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.propagate = False # lower levels are not propogated to children
    if log.hasHandlers():
        log.handlers.clear()
    # stream output
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh_format = logging.Formatter("%(message)s")
    sh.setFormatter(sh_format)
    log.addHandler(sh)
    # file output
    f = logging.FileHandler("data_collection.log")
    f.setLevel(logging.DEBUG)
    f_format = logging.Formatter("%(asctime)s - %(levelname)s\n%(message)s")
    f.setFormatter(f_format)
    log.addHandler(f)
    return log

if __name__ == "__main__":
    """
    Connects to and gathers data from the AirThings device
    """
    SerialNumber = int(sys.argv[1])
    main(SerialNumber)
