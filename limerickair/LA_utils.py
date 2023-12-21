#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 16:24:45 2023

@author: breandan
"""
import socket

from shapely.geometry.point import Point
from geopandas import GeoSeries

class LA_unit:
    def __init__(
            self,
            name = None,
            location = 'Limerick',
            loc_abbr = 'LK',
            fixed = True,
            ITM = Point(),
            latlong = Point()
            ):
        self.name = socket.gethostname() if name is None else name
        self.folder = f'./{self.name}'
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
    
    def ITM_to_latlong(self):
        gs_itm = GeoSeries([self.ITM], crs="EPSG:2157")
        gs_latlong = gs_itm.to_crs(crs="EPSG:4326")
        return gs_latlong[0]
    
    def latlong_to_ITM(self):
        gs_latlong = GeoSeries([self.latlong], crs="EPSG:4326")
        gs_itm = gs_latlong.to_crs(crs="EPSG:2157")
        return gs_itm[0]

# Uncomment the below, adjusting the values, 
# to define the sensor class instance here
# Otherwise set sensor class instance in __init.py__ or elsewhere

'''
LimerickAirXX = LA_unit(
    location='Limerick',
    loc_abbr='LK', 
    fixed=True,
    ITM = Point(),
    latlong = Point()
    )
'''