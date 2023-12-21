import threading
from shapely.geometry.point import Point  # noqa F401

from .LA_utils import LA_unit  # noqa F401
from .LA_BME280 import LA_BME280  # noqa F401
from .LA_PMS7003 import LA_PMS7003  # noqa F401
from .LA_GNSS import LA_GNSS  # noqa F401
from .LA_Analysis import LA_Analysis  # noqa F401

# Uncomment the below, adjusting the values,
# to define the sensor class instance here
# Otherwise set sensor class instance in LA_utils.py or elsewhere

if __name__ == "__main__":
    LimerickAirXX = LA_unit(
        location="Limerick", loc_abbr="LK", fixed=True, ITM=Point(), latlong=Point()
    )
    pm = threading.Thread(LimerickAirXX.record_pm())
    env = threading.Timer(60, LimerickAirXX.record_env())
    analysis = threading.Timer(86400, run_la_analysis())

    pm.start()
    env.start()
    analysis.start()

name = "limerickair"
__version__ = "0.1.1"
