#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 21:21:33 2023

@author: breandan

adapted from pigpio-serial-bb-examples/serial-bb-gps.py copyright paulv 2018-20

"""

import os
import socket

import pigpio

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