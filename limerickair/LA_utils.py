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
import time

from numbers import Number
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
        itm=Point(),
        latlong=Point(),
    ):
        self.name = socket.gethostname() if name is None else name
        self.folder = f"./{self.name}"
        os.makedirs(self.folder, exist_ok=True)
        self.location = location
        self.loc_abbr = loc_abbr
        self.fixed = fixed
        if self.fixed is True:
            if itm == Point() and latlong == Point():
                pass
            elif itm != Point() and latlong != Point():
                self.itm = itm
                self.latlong = latlong
            elif itm != Point() and latlong == Point():
                self.itm = itm
                self.latlong = self.itm_to_latlong()
            elif itm == Point() and latlong != Point():
                self.latlong = latlong
                self.itm = self.latlong_to_itm()
        #        if fixed:
        #            self.ITM = ITM if not ITM.is_empty else self.latlong_to_ITM()
        #            self.latlong = latlong if not latlong.is_empty else self.ITM_to_latlong()
        self.pm_sensor = LA_PMS7003(serialport="/dev/serial0")
        self.env_sensor = LA_BME280()
        self.pm_header = ["Timestamp", "PM2.5", "PM10"]
        self.env_header = ["Timestamp", "Temperature", "Pressure", "Humidity"]
        self.pm_env_header = [
            "Timestamp",
            "Temperature",
            "Pressure",
            "Humidity",
            "PM2.5",
            "PM10",
        ]

    def itm_to_latlong(self):
        gs_itm = GeoSeries([self.itm], crs="EPSG:2157")
        gs_latlong = gs_itm.to_crs(crs="EPSG:4326")
        return gs_latlong[0]

    def latlong_to_itm(self):
        gs_latlong = GeoSeries([self.latlong], crs="EPSG:4326")
        gs_itm = gs_latlong.to_crs(crs="EPSG:2157")
        return gs_itm[0]

    def _write_to_csv(self, filename, data, header=None):
        file_path = os.path.join(self.folder, filename)
        write_header = not os.path.exists(file_path) or os.stat(file_path).st_size == 0
        with open(file_path, "a", newline="") as f:
            csv_writer = csv.writer(f)
            if write_header and header:
                csv_writer.writerow(header)
            csv_writer.writerow(data)

    def get_pm(self):
        pm_data = self.pm_sensor.read_atm()
        return [dt.datetime.now(), pm_data["PM2.5_atm"], pm_data["PM10_atm"]]

    def record_pm(self, *args):
        while True:
            pm_reading = self.get_pm()
            filename = f"{self.name}_{pm_reading[0].isoformat()[:10]}_pm.csv"
            self._write_to_csv(filename, pm_reading, header=self.pm_header)
            if "once" in args:
                break
            if isinstance(args[0], Number) and args[0] > 0:
                time.sleep(args[0])

    def get_env(self):
        env_data = self.env_sensor.read_tph(smode="forced")
        return [
            dt.datetime.now(),
            env_data["temperature"],
            env_data["pressure"],
            env_data["humidity"],
        ]

    def record_env(self, *args):
        while True:
            env_reading = self.get_env()
            filename = f"{self.name}_{env_reading[0].isoformat()[:10]}_env.csv"
            self._write_to_csv(env_reading, filename, header=self.env_header)
            if "once" in args:
                break
            if isinstance(args[0], Number) and args[0] > 0:
                time.sleep(args[0])

    def get_pm_env(self):
        while True:
            now = dt.datetime.now()
            pm_data = self.pm_sensor.read_atm()
            env_data = self.env_sensor.read_tph(smode="forced")
            return [
                now,
                env_data["temperature"],
                env_data["pressure"],
                env_data["humidity"],
                pm_data["PM2.5_atm"],
                pm_data["PM10_atm"],
            ]

    def record_pm_env(self, *args):
        while True:
            pm_env_reading = self.get_pm_env()
            filename = f"{self.name}_{pm_env_reading[0].isoformat()[:10]}_pm_env.csv"
            self._write_to_csv(pm_env_reading, filename, header=self.pm_env_header)
            if "once" in args:
                break
            if isinstance(args[0], Number) and args[0] > 0:
                time.sleep(args[0])
