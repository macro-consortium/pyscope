from . import config
from . import convert

"""
Read and validate the expected config files from observatory.cfg
"""

values = None
valid_config = False

def read():
    global values
    global valid_config

    values = config.read("observatory.cfg")

    values.require_string("ascom_mount_driver")
    values.require("get_location_from_mount", bool)
    values.require_and_convert("latitude_degs", convert.from_dms)
    values.require_and_convert("longitude_degs", convert.from_dms)
    values.require_float("min_telescope_altitude_degs")
    values.require_float("settle_time_secs")


    valid_config = True


