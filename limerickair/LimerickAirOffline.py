import os
import socket
import csv

import datetime as dt

from LA_PMS7003 import LA_PMS7003
from LA_BME280 import LA_BME280

LA_unit = socket.gethostname()
if not os.path.exists(f'./{LA_unit}'):
    os.makedirs(f'./{LA_unit}')

pm_sensor = LA_PMS7003(serialport='/dev/serial0')
env_sensor = LA_BME280(sname=LA_unit)

def record_pm():
    while True:
        pm_data = pm_sensor.read_atm()
        pm_reading = [dt.datetime.now(),pm_data['PM2.5_atm'],pm_data['PM10_atm']]
        with open(f'./{LA_unit}/{LA_unit}_{pm_reading[0].isoformat()[:10]}_pm.csv', "a") as f:
            (csv.writer(f)).writerow(pm_reading)

def record_env():
    env_data = env_sensor.la_read_pth_forced()
    env_reading = [dt.datetime.now(),env_data['temperature'],env_data['pressure'],env_data['humidity']]
    with open(f'./{LA_unit}/{LA_unit}_{env_reading[0].isoformat()[:10]}_env.csv', "a", newline="") as f:
        (csv.writer(f)).writerow(env_reading)
        
def record_pm_env():
    while True:
        now = dt.datetime.now()
        pm_data = pm_sensor.read_atm()
        env_data = env_sensor.la_read_pth_forced()
        pm_env_reading = [now,env_data['temperature'],env_data['pressure'],env_data['humidity'],pm_data['PM2.5_atm'],pm_data['PM10_atm']]
        daily_file = f'./{LA_unit}/{LA_unit}_{pm_env_reading[0].isoformat[:10]}.csv'
        write_header = not os.path.exists(daily_file) or os.stat(daily_file).st_size == 0
        with open(daily_file, 'a', newline="") as f:
            if write_header:
                (csv.writer(f)).writerow(["Timestamp", "Temperature", "Pressure", "Humidity", "PM2.5", "PM10"])
            (csv.writer(f)).writerow(pm_env_reading)
            
record_pm_env()