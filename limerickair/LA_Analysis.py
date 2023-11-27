import sys
import dropbox
import pandas as pd
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, VPacker
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

import datetime as dt


class LA_Analysis:
    def __init__(
        self,
        sensor=None,
        date=None,
        LA_location=None,
        LA_location_long=None,
        LA_ITM_X=None,
        LA_ITM_Y=None,
        pm_csv=None,
        daily=True,
    ):
        self.LA_unit = sensor if sensor is not None else "LAxx"
        self.date = dt.date.today() - dt.timedelta(days=1) if date is None else date
        self.LA_location = LA_location if LA_location is not None else "xx"
        if LA_location_long is not None:
            self.LA_location_long = LA_location_long
        else:
            self.LA_location_long = "unspecified location"

        if pm_csv is None:
            try:
                self.pm_csv = (
                    f"./{self.LA_unit}/{self.LA_unit}_{self.date.isoformat()}_pm.csv"
                )
                self.read_pm_csv()
                self.read_env_csv()
                self.data_5m["Sensor"] = self.LA_unit
                if LA_ITM_X is not None:
                    self.LA_ITM_X = LA_ITM_X
                    self.data_5m["ITM_X"] = self.LA_ITM_X
                if LA_ITM_Y is not None:
                    self.LA_ITM_Y = LA_ITM_Y
                    self.data_5m["ITM_Y"] = self.LA_ITM_Y
                self.PM2_5_mean = self.pm_data.resample("1D").mean().iloc[0]["PM2.5"]
                self.PM10_mean = self.pm_data.resample("1D").mean().iloc[0]["PM10"]
                self.data_5m.to_csv(
                    f"./{self.LA_unit}/{self.LA_unit}_{(dt.date.today()-dt.timedelta(days=1)).isoformat()}_5m.csv"
                )
                self.create_graph()
                self.la_to_dropbox()
            except FileNotFoundError:
                return "CSV not found"

    def read_pm_csv(self):
        try:
            self.pm_data = pd.read_csv(
                self.pm_csv,
                sep=",",
                names=["Timestamp", "PM2.5", "PM10"],
                index_col="Timestamp",
                dtype={"PM2.5": np.int32, "PM10": np.int32},
                parse_dates=True,
            )
            self.data_5m = self.pm_data.resample("5Min").mean()
        except FileNotFoundError:
            pass

    def read_env_csv(self):
        try:
            self.env_csv = (
                f"./{self.LA_unit}/{self.LA_unit}_{self.date.isoformat()}_pm.csv"
            )
            self.env_data = pd.read_csv(
                self.env_csv,
                sep=",",
                names=["Timestamp", "Temperature", "Pressure", "Humidity"],
                index_col="Timestamp",
                dtype={
                    "Temperature": np.float64,
                    "Pressure": np.float64,
                    "Humidity": np.float64,
                },
                parse_dates=True,
            )
            self.data_5m[
                ["Temperature", "Pressure", "Humidity"]
            ] = self.env_data.resample("5Min").mean()
        except FileNotFoundError:
            pass

    def create_graph(self):
        fig, ax1 = plt.subplots()

        l2 = ax1.plot(
            self.data_5m["Temp"], linewidth=1, color="#e50000", label="Temperature (C)"
        )
        l3 = ax1.plot(
            self.data_5m["Humidity"], linewidth=1, color="#054e8a", label="Humidity (%)"
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
            "$\mathregular{PM_{2.5}}$ $\mathregular{(\u03bcg/m^{3}}$), $\mathregular{PM_{10}}$ $\mathregular{(\u03bcg/m^{3}}$), ",
            textprops=dict(
                color="#132237", size="small", rotation=90, ha="left", va="bottom"
            ),
        )
        ybox2 = TextArea(
            "Temperature (°C), ",
            textprops=dict(
                color="#e50000", size="small", rotation=90, ha="left", va="bottom"
            ),
        )
        ybox3 = TextArea(
            "Humidity (%)",
            textprops=dict(
                color="#054e8a", size="small", rotation=90, ha="left", va="bottom"
            ),
        )
        ybox = VPacker(children=[ybox3, ybox2, ybox1], align="bottom", pad=0, sep=0)
        anchored_ybox = AnchoredOffsetbox(
            loc="center left",
            child=ybox,
            pad=0.0,
            frameon=False,
            bbox_transform=ax1.transAxes,
            borderpad=-4,
        )
        ax1.add_artist(anchored_ybox)

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
            f"Particulate pollution {self.date}, {self.LA_location_long} ({self.LA_unit})",
            fontsize="medium",
            fontweight="bold",
        )

        plt.legend(
            handles=[l1[0], l6[0], l5[0], l2[0], l3[0], l4[0]],
            loc="lower left",
            bbox_to_anchor=(0.5, -0.5),
            ncol=2,
        )

        logo = plt.imread("logo.png")
        plt.figimage(logo)
        plt.savefig(
            f"./{self.LA_unit}/{self.LA_unit}_{self.date.isoformat()}.png",
            bbox_inches="tight",
        )

    def la_to_dropbox(self):
        # Establish list of files to upload
        upload_list = [
            f"./{self.LA_unit}/{self.LA_unit}_{(self.date).isoformat()}.csv",
            f"./{self.LA_unit}/{self.LA_unit}_{(self.date).isoformat()}_5m.csv"
            f"./{self.LA_unit}/{self.LA_unit}_{(self.date).isoformat()}.png",
        ]

        # Set path in Dropbox folder
        DBPATH = f"/Research/LimerickAir/{self.LA_unit}/"  # Keep the forward slash before destination filename

        # Create an instance of a Dropbox class, which can make requests to the API.

        # Access token
        TOKEN = "sl.BqUffC5nw1NPc79zfc9tGhB9X3wYkLhnGggEayROzZyCb-gPOO1Qk7_hv8t6wO0M6IhiC_NNEYudoOv7WRpMc4-S-EhyF7jH6ROGS3V79RkhLvQxA4SKWQZtCvo6fT52fXbCqyFX5s10"
        dbx = dropbox.Dropbox(TOKEN)

        # Check that the access token is valid
        try:
            dbx.users_get_current_account()
        except AuthError:
            sys.exit(
                "ERROR: Invalid access token; try re-generating an access token from the app console on the web."
            )

        # Create a backup of the current file
        for file_to_upload in upload_list:
            with open(file_to_upload, "rb") as f:
                # We use WriteMode=overwrite to make sure that the settings in the file are changed on upload
                BACKUPPATH = DBPATH + file_to_upload[2:]
                try:
                    dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode("overwrite"))
                except ApiError as err:
                    # This checks for the specific error where a user doesn't have
                    # enough Dropbox space quota to upload this file
                    if (
                        err.error.is_path()
                        and err.error.get_path().reason.is_insufficient_space()
                    ):
                        sys.exit("ERROR: Cannot back up; insufficient space.")
                    elif err.user_message_text:
                        print(err.user_message_text)
                        sys.exit()
                    else:
                        print(err)
                        sys.exit()
