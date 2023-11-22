import sys
import dropbox
import socket

from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

import datetime as dt

LA_unit = socket.gethostname()


def la_to_dropbox(
    upload_list=[
        f"./{LA_unit}/{LA_unit}_{(dt.date.today()-dt.timedelta(days=1)).isoformat()}.csv",
        f"./{LA_unit}/{LA_unit}_{(dt.date.today()-dt.timedelta(days=1)).isoformat()}_5m.csv"
        f"./{LA_unit}/{LA_unit}_{(dt.date.today()-dt.timedelta(days=1)).isoformat()}.png",
    ]
):
    # Set path in Dropbox folder
    DBPATH = f"/Research/LimerickAir/{LA_unit}/"  # Keep the forward slash before destination filename

    # Create an instance of a Dropbox class, which can make requests to the API.

    # Access token
    TOKEN = ""
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
