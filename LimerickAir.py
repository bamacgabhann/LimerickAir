"""
Includes code from Mark Benson's pms7003 module:

Read a Plantower PMS7003 serial sensor data.

A simple script to test the Plantower PMS7003 serial particulate sensor.

Outputs the various readings to the console.

Requires PySerial.

Edit the physical port variable to match the port you are using to connect to the sensor.

Updated to work on Python 3 (ord() is redundant)

Run with 'python pms7003.py'

The sensor payload is 32 bytes:

2 fixed start bytes (0x42 and 0x4d)
2 bytes for frame length
6 bytes for standard concentrations in ug/m3 (3 measurements of 2 bytes each)
6 bytes for atmospheric concentrations in ug/m3 (3 measurements of 2 bytes each)
12 bytes for counts per 0.1 litre (6 measurements of 2 bytes each)
1 byte for version
1 byte for error codes
2 bytes for checksum

MIT License

Copyright (c) 2018 Mark Benson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import os
import time
from datetime import datetime
import serial
import socket
import csv
import bme280

physicalPort = '/dev/serial0'

serialPort = serial.Serial(physicalPort)  # open serial port
# set hostname
AQ_unit = socket.gethostname()

# set location
from aqlocation import (AQ_location)

# Defining daily file writing function

def write_to_daily_file(row):
    # set date format
    YMD = datetime.now().strftime('%Y-%m-%d')
    # set file and folder root
    AQ_root = AQ_unit + '_' + YMD + '_' + AQ_location
    #make directory tree if it doesn't exist
    aq_year = datetime.now().strftime('%Y')
    aq_month = datetime.now().strftime('%m')
    aq_day = datetime.now().strftime('%d')
    directory = '/home/pi/AQoutput/' + aq_year + '/' + aq_month + '/' + aq_day
    if not os.path.exists(directory):
       os.makedirs(directory)
    # set file name
    file_name = AQ_root + '.csv'
    daily_file = os.path.join(directory, file_name)
    # open file and add data
    # write header row if needed
    write_header = not os.path.exists(daily_file) or os.stat(daily_file).st_size == 0
    if write_header:
        with open(daily_file, "a", newline="") as f_output:
            csv_output = csv.writer(f_output)
            csv_output.writerow(["Timestamp", "Temp", "Pressure", "Humidity", "PM2.5", "PM10"])
    # Write data to daily file
    with open(daily_file, "a", newline="") as f_output:
            csv_output = csv.writer(f_output)
            csv_output.writerow(row)

# function to read data from the Plantower PMS7003
while True:
    # Check if we have enough data to read a payload
    if serialPort.in_waiting >= 32:
        # Check that we are reading the payload from the correct place (i.e. the start bits)
        if ord(serialPort.read()) == 0x42 and ord(serialPort.read()) == 0x4d:

            # Read the remaining payload data
            data = serialPort.read(30)

            # Extract the byte data by summing the bit shifted high byte with the low byte
            # Use ordinals in python to get the byte value rather than the char value
            #print(data[1],data[1])
            #print("about to print out the 2 bytes corresponding to PM2.5")
            #print(data[4],data[5])
            #pm25 = data[4] + data[5]
            #intpm25 = int(pm25, base=16)
            #print(intpm25)
            frameLength = data[1] + (data[0] << 8)
            # Standard particulate values in ug/m3
            concPM1_0_CF1 = data[3] + (data[2] << 8)
            concPM2_5_CF1 = data[5] + (data[4] << 8)
            concPM10_0_CF1 = data[7] + (data[6] << 8)
            # Atmospheric particulate values in ug/m3
            concPM1_0_ATM = data[9] + (data[8] << 8)
            concPM2_5_ATM = data[11] + (data[10] << 8)
            concPM10_0_ATM = data[13] + (data[12] << 8)
            # Raw counts per 0.1l
            rawGt0_3um = data[15] + (data[14] << 8)
            rawGt0_5um = data[17] + (data[16] << 8)
            rawGt1_0um = data[19] + (data[18] << 8)
            rawGt2_5um = data[21] + (data[20] << 8)
            rawGt5_0um = data[23] + (data[22] << 8)
            rawGt10_0um = data[25] + (data[24] << 8)
            # Misc data
            version = data[26]
            errorCode = data[27]
            payloadChecksum = data[29] + (data[28] << 8)

            # Calculate the payload checksum (not including the payload checksum bytes)
            inputChecksum = 0x42 + 0x4d
            for x in range(0, 27):
                inputChecksum = inputChecksum + data[x]

            # read environmental data from the BME280
            temperature,pressure,humidity = bme280.readBME280All()

            # add the new data to the CSV file

            # Try 5 - use the function I defined
            row = [datetime.now(),temperature,pressure,humidity,str(concPM2_5_ATM),str(concPM10_0_ATM)]
            write_to_daily_file(row)



    time.sleep(0.7)  # Maximum recommended delay (as per data sheet)
