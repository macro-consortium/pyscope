from . import config
from . import convert

"""
Read and validate the expected config files from observatory.cfg
"""

valid_config = False

def read():
    global values
    values = config.read("observatory.cfg")

    # Ensure that all of the necessary values are present
    # and pass basic validation
    
    global telescope_name
    telescope_name = values.require_string("telescope_name")
    
    global origin
    origin = values.require_string("origin")
    
    global ascom_mount_driver
    ascom_mount_driver = values.require_string("ascom_mount_driver")
    
    global ascom_focuser_driver
    ascom_focuser_driver = values.require_string("ascom_focuser_driver")
    
    global camera_driver
    camera_driver = values.require_string("camera_driver")
    
    global autofocus_driver
    autofocus_driver = values.require_string("autofocus_driver")
    
    global weather_driver
    weather_driver = values.require_string("weather_driver")
    
    global get_location_from_mount
    get_location_from_mount = values.require("get_location_from_mount", bool)

    if not values.get_location_from_mount:
        global latitude_degs
        latitude_degs = values.require_and_convert("latitude_degs", convert.from_dms)

        global longitude_degs
        longitude_degs = values.require_and_convert("longitude_degs", convert.from_dms)
    
    global max_sun_altitude_degs
    max_sun_altitude_degs = values.require_float("max_sun_altitude_degs")

    global min_telescope_altitude_degs
    min_telescope_altitude_degs = values.require_float("min_telescope_altitude_degs")

    global settle_time_secs
    settle_time_secs = values.require_float("settle_time_secs")

    global max_focuser_error_counts
    max_focuser_error_counts = values.require_float("max_focuser_error_counts")

    global max_focuser_move_time_seconds
    max_focuser_move_time_seconds = values.require_float("max_focuser_move_time_seconds")

    global valid_config
    valid_config = True


