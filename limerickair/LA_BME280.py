import time
from smbus2 import SMBus
from bme280 import BME280


class LA_BME280(BME280):
    """
    Subclass of BME280 that provides additional methods for reading temperature, pressure, and humidity.

    Methods:
        la_read_tph: Read temperature, pressure, and humidity in forced mode.
    """

    def __init__(self):
        """
        Initialize the LA_BME280 object.
        """

        super().__init__(i2c_dev=SMBus(1))

    def read_tph(self, smode: str = "normal") -> dict:
        """
        Read temperature, pressure, and humidity.

        Args:
            smode: str
                Optional mode for reading (default: "normal").

        Returns:
            dict: Dictionary containing temperature, pressure, and humidity values.
        """

        self.setup(
            mode=smode,
            temperature_oversampling=1,
            pressure_oversampling=1,
            humidity_oversampling=1,
        )
        self._bme280.set("CTRL_MEAS", mode=smode)
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
