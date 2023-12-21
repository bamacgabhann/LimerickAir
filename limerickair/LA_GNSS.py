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
    """Dataclass for holding NMEA RMC protocol data fields"""

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
        self.utc = dt.datetime.strptime(self.hhmmss_ss, "%H%M%S.%f")
        self.strfutc = self.utc.strftime("%H:%M:%S.%f")
        self.mode, self.checksum = self.mode_cs.split("*")


@dataclass
class VTG:
    """Dataclass for holding NMEA VTG protocol data fields"""

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
        self.mode, self.checksum = self.mode_cs.split("*")


@dataclass
class GGA:
    """Dataclass for holding NMEA GGA protocol data fields"""

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
        self.utc = dt.datetime.strptime(self.hhmmss_ss, "%H%M%S.%f")
        self.strfutc = self.utc.strftime("%H:%M:%S.%f")
        self.DGPS, self.checksum = self.DGPS_cs.split("*")


@dataclass
class GSA:
    """Dataclass for holding NMEA GSA protocol data fields"""

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
        self.VDOP, self.checksum = self.VDOP_cs.split("*")


@dataclass
class GSV:
    """Dataclass for holding NMEA GSA protocol data fields"""

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
        self.SNR4, self.checksum = self.SNR4_cs.split("*")


@dataclass
class GLL:
    """Dataclass for holding NMEA GSA protocol data fields"""

    header: str
    latitude: str
    lat_direction: str
    longitude: str
    long_direction: str
    hhmmss_ss: str
    A_cs: str
    eol: str

    def __post_init__(self):
        self.utc = dt.datetime.strptime(self.hhmmss_ss, "%H%M%S.%f")
        self.strfutc = self.utc.strftime("%H:%M:%S.%f")
        self.A, self.checksum = self.A_cs.split("*")


class LA_NEO6M:
    def __init__(self, name=None, fixed=True, serialGPIO=24, baud=9600):
        self.name = socket.gethostname() if name is None else name
        self.folder = f"./{self.name}"
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
            except Exception:
                continue

            if bytes_read == 0:
                continue
            try:
                payload_str = payload.decode("utf-8", "ignore")
            except AttributeError:
                continue

            return payload_str

    def _compile_complete(self):
        payload_str = ""
        while True:
            payload_str = payload_str + self._read_bytes()
            i = payload_str.find("$GPRMC")
            if i > -1:
                payload_str = payload_str[i:]
                while True:
                    j = payload_str[1:].find("$GPRMC") + 1
                    if j > 0:
                        return payload_str[:j], payload_str[j:]

    # find a way to handle continuous reads
    # arg continuous = True, if True returns remnant?

    def read_gnss(self):
        reading = self._compile_complete()
        rmc0 = 0
        rmc1 = reading.find("\r\n")
        vtg0 = reading.find("$GPVTG")
        gga0 = reading.find("$GPGGA")
        gsa0 = reading.find("$GPGSA")
