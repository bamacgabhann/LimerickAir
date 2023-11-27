import os
import socket
import csv
import threading

import datetime as dt

from smbus2 import SMBus
from PMS7003 import PMS7003
import LA_BME280

LA_unit = socket.gethostname()
if not os.path.exists(f'./{LA_unit}'):
    os.makedirs(f'./{LA_unit}')

pm_sensor = PMS7003(serialport='/dev/serial0')
env_sensor = LA_BME280(i2c_dev=SMBus(1))

def record_pm():
    while True:
        pm_data = pm_sensor.read_all()
        pm_reading = [dt.datetime.now(),pm_data['PM2.5_atm'],pm_data['PM10_atm']]
        with open(f'./{LA_unit}/{LA_unit}_{pm_reading[0].isoformat()[:10]}_pm.csv', "a") as f:
            (csv.writer(f)).writerow(pm_reading)

def record_env():
    env_data = env_sensor.read_all()
    env_reading = [dt.datetime.now(),env_data['temperature'],env_data['pressure'],env_data['humidity']]
    with open(f'./{LA_unit}/{LA_unit}_{env_reading[0].isoformat()[:10]}_env.csv', "a", newline="") as f:
        (csv.writer(f)).writerow(env_reading)

pm = threading.Thread(record_pm())
env = threading.Timer(60, record_env())

pm.start()
env.start()