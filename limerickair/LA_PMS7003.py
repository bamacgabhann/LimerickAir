import serial
import struct


class LA_PMS7003(serial.Serial):
    def __init__(self, serialport=None, setbaudrate=9600):
        super().__init__(port=self.port, baudrate=self.baudrate)
        self.byte1 = 0x42
        self.byte2 = 0x4D
        self.frame_length = 0
        self.pm1_std = 1
        self.pm2_5_std = 2
        self.pm10_std = 3
        self.pm1_atm = 4
        self.pm2_5_atm = 5
        self.pm10_atm = 6
        self.pm0_3 = 7
        self.pm0_5 = 8
        self.pm1 = 9
        self.pm2_5 = 10
        self.pm5 = 11
        self.pm10 = 12
        self.version = 13
        self.error = 14
        self.check = 15

    def _check_waiting(self):
        if self.in_waiting >= 32:
            return True

    def _check_start(self):
        checkpayload = self.read(2)
        checkdata = struct.unpack("!BB", checkpayload)
        return checkdata[0] == self.byte1 and checkdata[1] == self.byte2

    def _read_(self):
        counter = 0
        while counter == 0:
            if self._check_waiting() is not True:
                continue
            if self._check_start() is not True:
                continue
            payload = self.read(30)
            if len(payload) < 30:
                continue
            reading = struct.unpack("!HHHHHHHHHHHHHBBH", payload)
            checksum = self.byte1 + self.byte2 + sum(payload[:-2])
            if checksum == reading[self.check]:
                return reading
            else:
                continue

    def _readbytes_(self):
        counter = 0
        while counter == 0:
            if self._check_waiting() is not True:
                continue
            if self._check_start() is not True:
                continue
            payload = self.read(30)
            if len(payload) < 30:
                continue
            return payload

    def read_all(self):
        reading = self._read_()
        return {
            "PM1_std": reading[self.pm1_std],
            "PM2.5_std": reading[self.pm2_5_std],
            "PM10_std": reading[self.pm10_std],
            "PM1_atm": reading[self.pm1_atm],
            "PM2.5_atm": reading[self.pm2_5_atm],
            "PM10_atm": reading[self.pm10_atm],
            "PM0_3_raw": reading[self.pm0_3],
            "PM0_5_raw": reading[self.pm0_5],
            "PM1_raw": reading[self.pm1],
            "PM2_5_raw": reading[self.pm2_5],
            "PM5_raw": reading[self.pm5],
            "PM10_raw": reading[self.pm10],
        }

    def read_atm(self):
        reading = self._read_()
        return {
            "PM1_atm": reading[self.pm1_atm],
            "PM2.5_atm": reading[self.pm2_5_atm],
            "PM10_atm": reading[self.pm10_atm],
        }

    def read_std(self):
        reading = self._read_()
        return {
            "PM1_std": reading[self.pm1_std],
            "PM2.5_std": reading[self.pm2_5_std],
            "PM10_std": reading[self.pm10_std],
        }

    def read_raw(self):
        reading = self._read_()
        return {
            "PM0_3_raw": reading[self.pm0_3],
            "PM0_5_raw": reading[self.pm0_5],
            "PM1_raw": reading[self.pm1],
            "PM2_5_raw": reading[self.pm2_5],
            "PM5_raw": reading[self.pm5],
            "PM10_raw": reading[self.pm10],
        }
