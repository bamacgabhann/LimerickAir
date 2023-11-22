import time
from smbus2 import SMBus
from bme280 import BME280


class LA_BME280(BME280):
    def __init__(i2c_dev=SMBus(1)):
        super().__init__(i2c_dev)

    def read_all(self):
        self.setup(
            mode="forced",
            temperature_oversampling=1,
            pressure_oversampling=1,
            humidity_oversampling=1,
        )
        self._bme280.set("CTRL_MEAS", mode="forced")
        while self._bme280.get("STATUS").measuring:
            time.sleep(0.001)

        raw = self._bme280.get("DATA")

        self.temperature = self.calibration.compensate_temperature(raw.temperature)
        self.pressure = self.calibration.compensate_pressure(raw.pressure) / 100.0
        self.humidity = self.calibration.compensate_humidity(raw.humidity)

        return {
            "temperature": self.temperature,
            "pressure": self.pressure,
            "humidity": self.humidity,
        }
