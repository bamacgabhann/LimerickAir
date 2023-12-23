import os
import time
import pandas as pd
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, VPacker

import datetime as dt


class LA_Analysis:
    def __init__(
        self,
        sensor=None,
        location=None,
        loc_abbr=None,
        itm=None,
        latlong=None,
        fixed=True,
        daily=True,
    ):
        self.sensor = sensor
        self.location = location
        self.loc_abbr = loc_abbr
        self.itm = itm
        self.latlong = latlong
        self.fixed = fixed
        self.daily = daily
        self.last_analysis = None
        self.data = None
        self.data_5m = None
        self.PM2_5_mean = None
        self.PM10_mean = None

    def analyse(
        self,
        sensor=None,
        date=dt.date.today() - dt.timedelta(days=1),
        pm=True,
        env=True,
        gnss=False,
        pm_env=False,
        daily=None,
    ):
        sensor = self.sensor if sensor is None else sensor
        daily = self.daily if daily is None else daily
        while daily:
            if self.last_analysis != dt.date.today():
                self._do_analysis(sensor, date, pm, env, gnss, pm_env)
                self.last_analysis = dt.date.today()
            time.sleep(3600)

        if not daily:
            self._do_analysis(sensor, date, pm, env, gnss, pm_env)

    @staticmethod
    def _pd_read_csv(csv, names, dtype):
        return pd.read_csv(
            csv,
            sep=",",
            names=names,
            index_col="Timestamp",
            dtype=dtype,
            parse_dates=True,
        )

    def _do_analysis(
        self,
        sensor,
        date,
        pm,
        env,
        gnss,
        pm_env,
    ):
        if pm_env is True:
            csv = f"./{sensor}/{sensor}_{date.isoformat()}_pm_env.csv"
            names = [
                "Timestamp",
                "Temperature",
                "Pressure",
                "Humidity",
                "PM2.5",
                "PM10",
            ]
            dtype = {
                "PM10": np.int32,
                "PM2.5": np.int32,
                "Temperature": np.float64,
                "Pressure": np.float64,
                "Humidity": np.float64,
            }
        elif pm is True:
            csv = f"./{sensor}/{sensor}_{date.isoformat()}_pm.csv"
            names = [
                "Timestamp",
                "PM2.5",
                "PM10",
            ]
            dtype = {
                "PM10": np.int32,
                "PM2.5": np.int32,
            }
        if os.path.exists(csv):
            self.data = self._pd_read_csv(csv=csv, names=names, dtype=dtype)
        if env is True:
            csv = f"./{sensor}/{sensor}_{date.isoformat()}_env.csv"
            names = [
                "Timestamp",
                "Temperature",
                "Pressure",
                "Humidity",
            ]
            dtype = {
                "Temperature": np.float64,
                "Pressure": np.float64,
                "Humidity": np.float64,
            }
            if os.path.exists(csv):
                self.env_data = self._pd_read_csv(csv=csv, names=names, dtype=dtype)
            self.data = self.data.join(self.env_data, how="outer")
            self.resample(sensor, date, gnss)
            self.create_graph(sensor, date, env=True)

    def resample(self, sensor, date, gnss=False):
        self.data_5m = self.data.resample("5Min").mean()
        self.PM2_5_mean = self.data.resample("1D").mean().iloc[0]["PM2.5"]
        self.PM10_mean = self.data.resample("1D").mean().iloc[0]["PM10"]
        if gnss is False:
            if self.itm.is_empty is False:
                self.data_5m["geometry"] = self.itm
            elif self.latlong.is_empty is False:
                self.data_5m["geometry"] = self.latlong
        self.data_5m.to_csv(f"./{sensor}/{sensor}_{date.isoformat()}_5m.csv")

    def create_graph(self, sensor, date, env):
        fig, ax1 = plt.subplots()
        if env is True:
            l2 = ax1.plot(
                self.data_5m["Temp"],
                linewidth=1,
                color="#e50000",
                label="Temperature (C)",
            )
            l3 = ax1.plot(
                self.data_5m["Humidity"],
                linewidth=1,
                color="#054e8a",
                label="Humidity (%)",
            )
        l5 = ax1.plot(
            self.data_5m["PM2.5"],
            linewidth=3,
            color="#ffffff",
            label="Average $\mathregular{PM_{2.5}=%.2f}$" % self.PM2_5_mean,
        )
        l1 = ax1.plot(
            self.data_5m["PM2.5"],
            linewidth=2,
            color="#132237",
            label="$\mathregular{PM_{2.5}}$ $\mathregular{(\u03bcg/m^{3}}$)",
        )
        l6 = ax1.plot(
            self.data_5m["PM10"],
            linewidth=2,
            linestyle=":",
            color="#132237",
            label="$\mathregular{PM_{10}}$ $\mathregular{(\u03bcg/m^{3}}$)",
        )

        # line at WHO limit
        ax1.axhline(
            y=15,
            linewidth=1.5,
            color="#840000",
            dashes=(2, 2),
            label="Daily average limit",
        )
        ax1.annotate(
            "WHO daily average guideline",
            color="#840000",
            xy=(ax1.get_xlim()[1], 17),
            horizontalalignment="right",
        )

        # daily average arrow
        ax1.annotate(
            "",
            (ax1.get_xlim()[0], self.PM2_5_mean),
            xytext=(-5, 0),
            textcoords="offset pixels",
            arrowprops=dict(arrowstyle="-|>"),
        )

        # AQIH background colours
        good1 = patches.Rectangle(
            (ax1.get_xlim()[0], 0),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            12,
            facecolor="#bfd730",
            alpha=0.3,
        )
        good2 = patches.Rectangle(
            (ax1.get_xlim()[0], 12),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            12,
            facecolor="#65b345",
            alpha=0.3,
        )
        good3 = patches.Rectangle(
            (ax1.get_xlim()[0], 24),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            12,
            facecolor="#328432",
            alpha=0.3,
        )
        fair1 = patches.Rectangle(
            (ax1.get_xlim()[0], 36),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            6,
            facecolor="#f2be1a",
            alpha=0.3,
        )
        fair2 = patches.Rectangle(
            (ax1.get_xlim()[0], 42),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            6,
            facecolor="#f7931e",
            alpha=0.3,
        )
        fair3 = patches.Rectangle(
            (ax1.get_xlim()[0], 48),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            6,
            facecolor="#f26522",
            alpha=0.3,
        )
        poor1 = patches.Rectangle(
            (ax1.get_xlim()[0], 54),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            5,
            facecolor="#ed1c24",
            alpha=0.3,
        )
        poor2 = patches.Rectangle(
            (ax1.get_xlim()[0], 59),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            6,
            facecolor="#b11117",
            alpha=0.3,
        )
        poor3 = patches.Rectangle(
            (ax1.get_xlim()[0], 65),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            6,
            facecolor="#743618",
            alpha=0.3,
        )
        vpoor = patches.Rectangle(
            (ax1.get_xlim()[0], 71),
            ax1.get_xlim()[1] - ax1.get_xlim()[0],
            ax1.get_ylim()[1] - 71,
            facecolor="#b43f97",
            alpha=0.5,
        )

        ax1.add_patch(good1)
        ax1.add_patch(good2)
        ax1.add_patch(good3)
        ax1.add_patch(fair1)
        ax1.add_patch(fair2)
        ax1.add_patch(fair3)
        ax1.add_patch(poor1)
        ax1.add_patch(poor2)
        ax1.add_patch(poor3)
        ax1.add_patch(vpoor)

        ybox1 = TextArea(
            "$\mathregular{PM_{2.5}}$ $\mathregular{(\u03bcg/m^{3}}$), $\mathregular{PM_{10}}$ $\mathregular{(\u03bcg/m^{3}}$)",
            textprops=dict(
                color="#132237", size="small", rotation=90, ha="left", va="bottom"
            ),
        )
        children = [ybox1]
        if env is True:
            ybox3 = TextArea(
                "Temperature (°C), ",
                textprops=dict(
                    color="#e50000", size="small", rotation=90, ha="left", va="bottom"
                ),
            )
            ybox2 = TextArea(
                "Humidity (%), ",
                textprops=dict(
                    color="#054e8a", size="small", rotation=90, ha="left", va="bottom"
                ),
            )
            children = [ybox1, ybox2, ybox3]
        ybox = VPacker(children=children, align="bottom", pad=0, sep=0)
        anchored_ybox = AnchoredOffsetbox(
            loc="center left",
            child=ybox,
            pad=0.0,
            frameon=False,
            bbox_transform=ax1.transAxes,
            borderpad=-4,
        )
        ax1.add_artist(anchored_ybox)

        if env is True:
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

            ax2.set_ylabel(
                "Pressure (mB)", color="#4b006e"
            )  # we already handled the x-label with ax1
            l4 = ax2.plot(
                self.data_5m["Pressure"],
                linewidth=1,
                color="#4b006e",
                label="Pressure (mB)",
            )
            ax2.set_ylim(950, 1050)
            ax2.tick_params(axis="y", labelcolor="#4b006e")

        # beautify the x-labels
        plt.margins(x=0)
        plt.gcf().autofmt_xdate()
        myFmt = mdates.DateFormatter("%H:%M")
        hours = mdates.HourLocator(interval=2)
        plt.gca().xaxis.set_major_locator(hours)
        plt.gca().xaxis.set_major_formatter(myFmt)

        ax1.tick_params(axis="y", labelcolor="#2db464")

        plt.title(
            f"Particulate pollution {date} {self.location} ({sensor})",
            fontsize="medium",
            fontweight="bold",
        )

        plt.legend(
            handles=[l1[0], l6[0], l5[0]]
            if env is False
            else [l1[0], l6[0], l5[0], l2[0], l3[0], l4[0]],
            loc="lower left",
            bbox_to_anchor=(0.5, -0.5),
            ncol=2,
        )

        logo = plt.imread("logo.png")
        plt.figimage(logo)
        plt.savefig(
            f"./{self.sensor}/{self.sensor}_{date.isoformat()}.png",
            bbox_inches="tight",
        )
