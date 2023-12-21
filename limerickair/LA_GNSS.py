#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 21:21:33 2023

@author: breandan

adapted from pigpio-serial-bb-examples/serial-bb-gps.py copyright paulv 2018-20
https://github.com/paulvee/pigpio-serial-bb-examples/blob/main/serial_bb_gps.py
"""

import os
import socket
import datetime as dt
from dataclasses import dataclass
import pigpio

@dataclass
class RMC:
    '''Dataclass for holding NMEA RMC protocol data fields'''
    header: str
    hhmmss_ss: str
    status: str
    latitude: str
    lat_direction: str
    longitude: str
    long_direction: str
    SOG: str
    COG: str
    ddmmyy: str
    magvar: str
    magvar_direction: str
    mode_cs: str
    eol: str
    
    def __post_init__(self):
        self.utc = dt.strptime(self.hhmmss_ss, '%H%M%S.%f')
        self.strfutc = self.utc.strftime('%H:%M:%S.%f')
        self.mode, self.checksum = self.mode_cs.split('*')

@dataclass
class VTG:
    '''Dataclass for holding NMEA VTG protocol data fields'''
    header: str
    COGT: str
    T: str
    COGm: str
    M: str
    SOG: str
    N: str
    kph: str
    K: str
    mode_cs: str
    eol: str

    def __post_init__(self):
        self.mode, self.checksum = self.mode_cs.split('*')

@dataclass
class GGA:
    '''Dataclass for holding NMEA GGA protocol data fields'''
    header: str
    hhmmss_ss: str
    latitude: str
    longitude: str
    fix_status: str
    NoSV: str
    HDOP: str
    altitude: str
    alt_units: str
    geoid_altitude: str
    geoid_alt_units: str
    diff_age: str
    DGPS_cs: str
    eol: str

    def __post_init__(self):
        self.utc = dt.strptime(self.hhmmss_ss, '%H%M%S.%f')
        self.strfutc = self.utc.strftime('%H:%M:%S.%f')
        self.DGPS, self.checksum = self.DGPS_cs.split('*')

@dataclass
class GSA:
    '''Dataclass for holding NMEA GSA protocol data fields'''
    header: str
    s_smode: str
    fix_status: str
    sv1: str
    sv2: str
    sv3: str
    sv4: str
    sv5: str
    sv6: str
    sv7: str
    sv8: str
    sv9: str
    sv10: str
    sv11: str
    sv12: str
    PDOP: str
    HDOP: str
    VDOP_cs: str
    eol: str

    def __post_init__(self):
        self.VDOP, self.checksum = self.VDOP_cs.split('*')

@dataclass
class GSV:
    '''Dataclass for holding NMEA GSA protocol data fields'''
    header: str
    number_messages: str
    msg_no: str
    no_SV: str
    PRN1: str
    elevation1: str
    azimuth1: str
    SNR1: str
    PRN2: str
    elevation2: str
    azimuth2: str
    SNR2: str
    PRN3: str
    elevation3: str
    azimuth3: str
    SNR3: str
    PRN4: str
    elevation4: str
    azimuth4: str
    SNR4_cs: str
    eol: str

    def __post_init__(self):
        self.SNR4, self.checksum = self.SNR4_cs.split('*')

@dataclass
class GLL:
    '''Dataclass for holding NMEA GSA protocol data fields'''
    header: str
    latitude: str
    lat_direction: str
    longitude: str
    long_direction: str
    hhmmss_ss: str
    A_cs: str
    eol: str
    
    def __post_init__(self):
        self.utc = dt.strptime(self.hhmmss_ss, '%H%M%S.%f')
        self.strfutc = self.utc.strftime('%H:%M:%S.%f')
        self.A, self.checksum = self.A_cs.split('*')

class LA_NEO6M:
    def __init__(
            self,
            name = None,
            fixed = True,
            serialGPIO = 24,
            baud = 9600
            ):
        if name is None:
            self.name = socket.gethostname()
        else:
            self.name = name
        self.folder = f'./{self.name}'
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.fixed = fixed
        self.serialGPIO = serialGPIO
        self.baud = baud
        self.serial = pigpio.pi(self.name)
        self.serial.set_mode(self.serialGPIO, pigpio.INPUT)

    
    def _read_bytes(self):
        try:
            self.serial.bb_serial_read_close(self.serialGPIO)
        except pigpio.error:
            self.serial.bb_serial_read_open(self.serialGPIO, self.baud)

        while True:
            try:
                (bytes_read, payload) = self.serial.bb_serial_read(self.serialGPIO)
            except:
                continue

            if bytes_read == 0:
                continue
            else:
                try:
                    payload_str = payload.decode("utf-8", "ignore")
                except AttributeError:
                    continue
                
                return payload_str

    def _compile_complete(self):
        
        payload_str = ''
        while True:
            payload_str = payload_str + self._read_bytes()
            i = payload_str.find('$GPRMC')
            if i > -1:
                payload_str = payload_str[i:]
                while True:
                    j = payload_str[1:].find('$GPRMC') + 1
                    if j > 0:
                        return (payload_str[:j], payload_str[j:])

# find a way to handle continuous reads
# arg continuous = True, if True returns remnant?

    def read_gnss(self):
        
        reading = self._compile_complete()
        rmc0 = 0
        rmc1 = reading.find('\r\n')
        vtg0 = reading.find('$GPVTG')
        gga0 = reading.find('$GPGGA')
        gsa0 = reading.find('$GPGSA')
        
        











LA_unit = socket.gethostname()

folder = f'./{LA_unit}'

if not os.path.exists(folder):
    os.makedirs(f'./{LA_unit}')

serialGPIO = 24
line_start = '$'
line_end = '\r'

while True:
    try:
        serial2 = pigpio.pi(LA_unit)
        serial2.set_mode(serialGPIO, pigpio.INPUT)
    except AttributeError:
        continue

def right(s, amount):
    return s[amount:]

def left(s, amount):
    return s[:amount]

def mid(s, offset, amount):
    return s[offset-1:offset+amount-1]


def main():


    str_s = ""  # holds the string building of segments
    str_r = ""  # holds the left-over from a previous string which may contain
                # the start of a new sentence
    
    try:
        serial2.bb_serial_read_close(serialGPIO)
    except:
        pass

    serial2.bb_serial_read_open(serialGPIO, 9600)

    try:
        while True:
            # get some data. The bb_serial_read will read small segments of the string
            # they need to be added together to form a complete sentence.
            (count, data) = serial2.bb_serial_read(serialGPIO)

            # wait for the start of a new sentence, it starts with a line_start
            if (int(count) == 0): # wait for real data
                continue
            
            # we have data
            # decode to ascii first so we can use string functions
            
            try:
                data_s = data.decode("utf-8", "ignore") # discard non-ascii data

            except AttributeError:
                continue
            
            # add the left-over from the previous string if there was one
            data_s = str_r + data_s

            #  look for the line_start in this segment
            if line_start in data_s:

                pos = data_s.find(line_start)  # get the position of the line_start
                
                # save the start of the sentence starting with line_start
                str_s = right(data_s, pos)  # strip everything to the left
                
                # look to see if there are more line_start's in this segment
                if str_s.count(line_start) > 1 :   # there is another one!
                    # skip the first and get the position of the second line_start
                    pos = str_s[1:].find(line_start)

                    # strip everything to the left of the second line_start
                    str_s = right(str_s, pos+1)


                # get more data segments to complete the sentence
                while (int(count) > 0):

                    (count, data) = serial2.bb_serial_read(serialGPIO)

                    if int(count) == 0 : # only process real data
                        count = 1  # stay in this while loop
                        continue
                    
                    # decode to ascii
                    try:
                        data_s = data.decode("utf-8", "ignore")
                    except ValueError.ParseError:
                        continue

                    # look for the line_end "\r" of the sentence
                    if line_end in data_s:

                        pos = data_s.find(line_end)

                        str_r = left(data_s, pos)  # use everything to the left of the line_end
                        str_s = str_s +  str_r     # finish the sentence

#                        parseGPS(str_s)
                        if 'GPRMC' in str_s:
                            rmc_header, rmc_time_utc, rmc_status, rmc_lat, rmc_lat_ns, rmc_long, rmc_long_ew, rmc_spd_kts, rmc_heading_deg, rmc_date, rmc_magvar, rmc_magvar_ew, rmc_mode_cs = str_s.split(',')
                            with open(f'./{LA_unit}/{LA_unit}_gnss_test3.txt', 'a') as f:
                                f.write(f'rmc_lat = {rmc_lat}, rmc_long = {rmc_long}')
#                       elif 'GPVTG' in str_s:
#                            vtg_header,vtg_cogt,vtg_T,vtg_cogm,vtg_M,vtg_sog,vtg_N,vtg_kph,vtg_K,vtg_mode_cs = str_s.split(',')
#                            with open(f'./{LA_unit}/{LA_unit}_gnss_test3.txt', 'a') as f:
#                                f.write(f'vtg_lat = {rmc_lat}, rmc_long = {rmc_long}')
                        elif 'GPGGA' in str_s:
                            gga_header,gga_time,gga_lat,gga_ns,gga_long,gga_ew,gga_FS,gga_NoSV,gga_HDOP,gga_msl,gga_m,gga_Altref,gga_m,gga_DiffAge,gga_DiffStation_cs = str_s.split(',')
                            with open(f'./{LA_unit}/{LA_unit}_gnss_test3.txt', 'a') as f:
                                f.write(f'gga_lat = {gga_lat}, gga_long = {gga_long}')
                        elif 'GPGLL' in str_s:
                            gll_header,gll_lat,gll_ns,gll_long,gll_ew,gll_time,gll_A,gll_cs = str_s.split(',')
                            with open(f'./{LA_unit}/{LA_unit}_gnss_test3.txt', 'a') as f:
                                f.write(f'gll_lat = {gll_lat}, gll_long = {gll_long}')
                        else:
                            pass
                        
                        # save the left-over, which can be the start of a new sentence
                        str_r = right(data_s, pos+1)
                        # if we have a single "\n", discard it
                        if str_r == "\n" :
                            str_r = ""   # skip the \n part of the line_end

                        # start looking for a line_start again
                        break
                    
                    else:
                        # add the segments together
                        str_s = str_s +  data_s
                        # get more segments to complete the sentence

            else:
                # continue looking for the start of a segment
                str_s = ""
                data_s = ""
                continue


    except KeyboardInterrupt: # Ctrl-C
        os._exit(130)

    except Exception:
        os._exit(130)

main()

#with open(f'./{LA_unit}/{LA_unit}_gnss_test.txt', 'a') as f:
#    f.write(f'count = {count}\n data = {data}')