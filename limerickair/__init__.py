import threading
from shapely.geometry.point import Point  # noqa F401

from .LA_utils import LA_unit  # noqa F401
from .LA_BME280 import LA_BME280  # noqa F401
from .LA_PMS7003 import LA_PMS7003  # noqa F401
from .LA_GNSS import LA_GNSS  # noqa F401
from .LA_Analysis import LA_Analysis  # noqa F401


LimerickAir = LA_unit(
    location="Limerick", loc_abbr="LK", fixed=True, itm=Point(), latlong=Point()
)
analyser = LA_Analysis(
    sensor=LimerickAir.name,
    location=LimerickAir.location,
    loc_abbr=LimerickAir.loc_abbr,
    itm=LimerickAir.itm,
    latlong=LimerickAir.latlong,
    fixed=LimerickAir.fixed,
    daily=True,
)


def daily_analysis():
    analyser.analyse(
        sensor=LimerickAir.name, pm=True, env=True, gnss=False, pm_env=False, daily=True
    )


def main():
    pm = threading.Thread(target=LimerickAir.record_pm, args=[0])
    env = threading.Thread(target=LimerickAir.record_env, args=[60])
    analysis = threading.Thread(target=daily_analysis, args=[])
    pm.start()
    env.start()
    analysis.start()


if __name__ == "__main__":
    main()

name = "limerickair"
__version__ = "0.1.1"
