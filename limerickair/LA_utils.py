#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 16:24:45 2023

@author: breandan
"""
import os
import socket
import csv
import datetime as dt
from shapely.geometry.point import Point
from geopandas import GeoSeries

from LA_PMS7003 import LA_PMS7003
from LA_BME280 import LA_BME280


class LA_unit:
    def __init__(
        self,
        name=None,
        location="Limerick",
        loc_abbr="LK",
        fixed=True,
        ITM=Point(),
        latlong=Point(),
    ):
        self.name = socket.gethostname() if name is None else name
        self.folder = f"./{self.name}"
        if not os.path.exists(f"./{LA_unit}"):
            os.makedirs(f"./{LA_unit}")
        self.location = location
        self.loc_abbr = loc_abbr
        self.fixed = fixed
        if self.fixed is True:
            if ITM == Point() and latlong == Point():
                pass
            elif ITM != Point() and latlong != Point():
                self.ITM = ITM
                self.latlong = latlong
            elif ITM != Point() and latlong == Point():
                self.ITM = ITM
                self.latlong = self.ITM_to_latlong()
            elif ITM == Point() and latlong != Point():
                self.latlong = latlong
                self.ITM = self.latlong_to_ITM()
        self.pm_sensor = LA_PMS7003(serialport="/dev/serial0")
        self.env_sensor = LA_BME280()

    def ITM_to_latlong(self):
        gs_itm = GeoSeries([self.ITM], crs="EPSG:2157")
        gs_latlong = gs_itm.to_crs(crs="EPSG:4326")
        return gs_latlong[0]

    def latlong_to_ITM(self):
        gs_latlong = GeoSeries([self.latlong], crs="EPSG:4326")
        gs_itm = gs_latlong.to_crs(crs="EPSG:2157")
        return gs_itm[0]

    def record_pm(self):
        while True:
            pm_data = self.pm_sensor.read_atm()
            pm_reading = [dt.datetime.now(), pm_data["PM2.5_atm"], pm_data["PM10_atm"]]
            with open(
                f"./{LA_unit}/{LA_unit}_{pm_reading[0].isoformat()[:10]}_pm.csv", "a"
            ) as f:
                (csv.writer(f)).writerow(pm_reading)

    def record_env(self):
        env_data = self.env_sensor.read_tph(smode="forced")
        env_reading = [
            dt.datetime.now(),
            env_data["temperature"],
            env_data["pressure"],
            env_data["humidity"],
        ]
        with open(
            f"./{LA_unit}/{LA_unit}_{env_reading[0].isoformat()[:10]}_env.csv",
            "a",
            newline="",
        ) as f:
            (csv.writer(f)).writerow(env_reading)

    def record_pm_env(self):
        while True:
            now = dt.datetime.now()
            pm_data = self.pm_sensor.read_atm()
            env_data = self.env_sensor.read_tph(smode="forced")
            pm_env_reading = [
                now,
                env_data["temperature"],
                env_data["pressure"],
                env_data["humidity"],
                pm_data["PM2.5_atm"],
                pm_data["PM10_atm"],
            ]
            daily_file = f"./{LA_unit}/{LA_unit}_{pm_env_reading[0].isoformat[:10]}.csv"
            write_header = (
                not os.path.exists(daily_file) or os.stat(daily_file).st_size == 0
            )
            with open(daily_file, "a", newline="") as f:
                if write_header:
                    (csv.writer(f)).writerow(
                        [
                            "Timestamp",
                            "Temperature",
                            "Pressure",
                            "Humidity",
                            "PM2.5",
                            "PM10",
                        ]
                    )
                (csv.writer(f)).writerow(pm_env_reading)


# Uncomment the below, adjusting the values,
# to define the sensor class instance here
# Otherwise use sensor class instance in __init.py__
# or define elsewhere

"""
LimerickAirXX = LA_unit(
    location='Limerick',
    loc_abbr='LK', 
    fixed=True,
    ITM = Point(),
    latlong = Point()
    )
"""
