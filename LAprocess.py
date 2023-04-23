import os
import datetime
import socket
import pandas as pd  # TODO: Use geopandas or polars?
import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# TODO: do i need all these separate imports of matplotlib?
# stop ssh display errors
matplotlib.use('Agg')


# import file name variables
YMD = datetime.datetime.now().strftime('%Y-%m-%d')
AQ_unit = socket.gethostname()
from aqlocation import (AQ_location, AQ_location_long, ITM_X, ITM_Y)

# TODO: use GNSS to set coordinates

# set for yesterday

from datetime import datetime, timedelta
y_date = datetime.now() - timedelta(1)
yYMD = y_date.strftime('%Y-%m-%d')

#make a variable with the file name to be analysed
y_root = AQ_unit + '_' + yYMD + '_' + AQ_location

# change working directory
y_year = y_date.strftime('%Y')
y_month = y_date.strftime('%m')
y_day = y_date.strftime('%d')
directory = '/home/pi/AQoutput/' + y_year + '/' + y_month + '/' + y_day
y_csv = y_root + '.csv'
y_daily_file = os.path.join(directory, y_csv)

# Read data from csv
aqdata = pd.read_csv(y_daily_file, index_col='Timestamp', parse_dates=True)

# create second data frame which is the 5 min averages
aqdata_5min = aqdata.resample('5Min').mean()
aqdata_5min['X'] = ITM_X
aqdata_5min['Y'] = ITM_Y
aqdata_5min['Sensor'] = AQ_unit

# calculate daily average
aqdata_daily = aqdata.resample('D').mean()
pm_daily = aqdata_daily.iloc[0]['PM2.5']
pm_daily_str = str("%.2f" % pm_daily)

# filename for new output csv from 5 min average data frame
y_filename_5m = y_root + '_5m.csv'
y_csv_5m = os.path.join(directory, y_filename_5m)
# export 5 min data frame to the new csv
aqdata_5min.to_csv(y_csv_5m, header=["Temp", "Pressure", "Humidity", "PM2.5", "PM10", "X", "Y", "Sensor"])

# code for graph, draft

# define x axis as dates
aq_times = mdates.date2num(aqdata_5min.index.to_pydatetime())


#draw graphs for each y axis

fig, ax1 = plt.subplots()

ax1.set_xlabel('Time')
ax1.set_ylabel('PM2.5 (ug/m3), Temperature (C), Humidity (%)', color='#132237')
l2 = ax1.plot_date(aq_times, 'Temp', data=aqdata_5min, fmt='-', linewidth=1, color='#e50000', label='Temperature (C)')
l3 = ax1.plot_date(aq_times, 'Humidity', data=aqdata_5min, fmt='-', linewidth=1, color='#054e8a', label='Humidity (%)')
l5  = ax1.plot_date(aq_times, 'PM2.5', data=aqdata_5min, fmt='-', linewidth=3, color='#ffffff')
l1 = ax1.plot_date(aq_times, 'PM2.5', data=aqdata_5min, fmt='-', linewidth=2, color='#132237', label='PM2.5 (ug/m3)')

# line at 25ug
ax1.axhline(y=25, linewidth=1.5, color='#840000', label="Daily average limit")
ax1.annotate('WHO daily average guideline', color='#840000', xy=(ax1.get_xlim()[1], 27), horizontalalignment='right')

# line for daily average
dpos = pm_daily + 2
ax1.axhline(y=pm_daily, linewidth=1, color='#ffffff', label="Measured daily average")
ax1.annotate('Measured daily average', color='#ffffff', xy=(aq_times[0], dpos))

# AQIH background colours

good1 = patches.Rectangle((ax1.get_xlim()[0], 0), ax1.get_xlim()[1] - ax1.get_xlim()[0], 11, facecolor='#bfd730', alpha=0.5)
good2 = patches.Rectangle((ax1.get_xlim()[0], 11), ax1.get_xlim()[1] - ax1.get_xlim()[0], 23, facecolor='#65b345', alpha=0.5)
good3 = patches.Rectangle((ax1.get_xlim()[0], 24), ax1.get_xlim()[1] - ax1.get_xlim()[0], 35, facecolor='#328432', alpha=0.5)
fair1 = patches.Rectangle((ax1.get_xlim()[0], 36), ax1.get_xlim()[1] - ax1.get_xlim()[0], 41, facecolor='#f2be1a', alpha=0.5)
fair2 = patches.Rectangle((ax1.get_xlim()[0], 42), ax1.get_xlim()[1] - ax1.get_xlim()[0], 47, facecolor='#f7931e', alpha=0.5)
fair3 = patches.Rectangle((ax1.get_xlim()[0], 48), ax1.get_xlim()[1] - ax1.get_xlim()[0], 53, facecolor='#f26522', alpha=0.5)
poor1 = patches.Rectangle((ax1.get_xlim()[0], 54), ax1.get_xlim()[1] - ax1.get_xlim()[0], 58, facecolor='#ed1c24', alpha=0.5)
poor2 = patches.Rectangle((ax1.get_xlim()[0], 59), ax1.get_xlim()[1] - ax1.get_xlim()[0], 64, facecolor='#b11117', alpha=0.5)
poor3 = patches.Rectangle((ax1.get_xlim()[0], 65), ax1.get_xlim()[1] - ax1.get_xlim()[0], 70, facecolor='#743618', alpha=0.5)
vpoor = patches.Rectangle((ax1.get_xlim()[0], 71), ax1.get_xlim()[1] - ax1.get_xlim()[0], ax1.get_ylim()[1], facecolor='#b43f97', alpha=0.5)

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

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

ax2.set_ylabel('Pressure (mB)', color='#4b006e')  # we already handled the x-label with ax1
l4 = ax2.plot_date(aq_times, 'Pressure', data=aqdata_5min, fmt='-', linewidth=1, color='#4b006e', label='Pressure (mB)')
ax2.set_ylim(950, 1050)
ax2.tick_params(axis='y', labelcolor='#4b006e')

# beautify the x-labels
plt.gcf().autofmt_xdate()
myFmt = mdates.DateFormatter('%H:%M')
hours = mdates.HourLocator(interval = 2)
plt.gca().xaxis.set_major_locator(hours)
plt.gca().xaxis.set_major_formatter(myFmt)

ax1.tick_params(axis='y', labelcolor='#2db464')

# Add title and legend
plt.title('Particulate pollution' + ' ' + yYMD + ' ' + AQ_unit + ' ' + AQ_location_long)
plt.legend(handles=[l1[0], l2[0], l3[0], l4[0]], loc='lower left', bbox_to_anchor=(0.5, -0.4), ncol=2)
logo = plt.imread('logo.png')
plt.figimage(logo)

# set file names and path for export
y_png_name = y_root + '.png'
y_pdf_name = y_root + '.pdf'
y_png = os.path.join(directory, y_png_name)
y_pdf = os.path.join(directory, y_pdf_name)

# save PNG
plt.savefig(y_png, bbox_inches='tight')

# save PDF
plt.savefig(y_pdf, bbox_inches='tight')



plt.close()


# TODO: Here add code to post on Mastodon




# Upload to Dropbox
# TODO: make this a function

import sys
import dropbox

from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

# Change working directory
os.chdir(directory)

# Establish list of files to upload
upload_list = [y_csv, y_filename_5m, y_png_name, y_pdf_name]

# Set path in Dropbox folder
DBPATH = '/Research/LimerickAir/' + AQ_unit + '/' + y_year + '/' + y_month + '/' + y_day + '/' # Keep the forward slash before destination filename

# Create an instance of a Dropbox class, which can make requests to the API.

# Access token

from .la_secrets import TOKEN
dbx = dropbox.Dropbox(TOKEN)

# Check that the access token is valid
try:
    dbx.users_get_current_account()
except AuthError:
    sys.exit(
        "ERROR: Invalid access token; try re-generating an access token from the app console on the web.")

  
# Create a backup of the current file
for file_to_upload in upload_list:
    with open(file_to_upload, 'rb') as f:
        # We use WriteMode=overwrite to make sure that the settings in the file are changed on upload
        BACKUPPATH = DBPATH + file_to_upload
        try:
            dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                    err.error.get_path().error.is_insufficient_space()):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                sys.exit()
            else:
                sys.exit()
