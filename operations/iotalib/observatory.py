# Built-in Python imports
import datetime
import logging
import math
import time

# Third-party imports
import ephem
from win32com.client import Dispatch

# iotalib imports
from . import comhelper
from . import config_observatory
from . import config_focus_offsets
from . import weather_thread

maxim = None   # Reference to MaxIm.Application object
camera = None  # Reference to a camera driver (one of the camera_* modules in the drivers directory)
mount = None   # Reference to ASCOM Telescope object
focuser = None   # Reference to ASCOM Focuser object
weather = None # Reference to a weather driver (one of the weather_* modules in the drivers directory)
dome_monitor = None  # TODO
autofocus = None # Reference to an autofocus driver (one of the autofocus_* modules in the drivers directory)

def setup_camera():
    global camera

    camera_driver_name = config_observatory.values.camera_driver
    if camera_driver_name == "camera_maxim":
        from .drivers import camera_maxim
        camera = camera_maxim
    else:
        raise Exception("Unrecognized camera driver: %s" % camera_driver_name)

    camera.initialize()

def setup_mount():
    global mount

    mount_id = config_observatory.values.ascom_mount_driver
    logging.info("Connecting to mount %s", mount_id)
    mount = Dispatch(mount_id)
    mount.Connected = True

    if config_observatory.values.get_location_from_mount:
        logging.info("Reading latitude and longitude from mount driver")
        config_observatory.values.latitude_degs = mount.SiteLatitude
        config_observatory.values.longitude_degs = mount.SiteLongitude

    logging.info("Latitude = %f", config_observatory.values.latitude_degs)
    logging.info("Longitude = %f", config_observatory.values.longitude_degs)

def setup_focuser():
    global focuser

    focuser_id = config_observatory.values.ascom_focuser_driver
    logging.info("Connecting to focuser %s", focuser_id)
    focuser = Dispatch(focuser_id)
    focuser.Connected = True

    logging.info("Connected to focuser. Current position = %s", focuser.Position)

def setup_autofocus():
    global autofocus

    autofocus_driver_name = config_observatory.values.autofocus_driver
    if autofocus_driver_name == "autofocus_pwi":
        from .drivers import autofocus_pwi
        autofocus = autofocus_pwi
        autofocus.initialize()
    elif autofocus_driver_name == "autofocus_simulator":
        from .drivers import autofocus_simulator
        autofocus = autofocus_simulator
        autofocus.initialize(camera)
    else:
        raise Exception("Unrecognized autofocus driver: %s" % autofocus_driver_name)

def setup_weather():
    """
    Load the weather driver and launch a background thread
    to monitor the weather
    """

    global weather

    weather_driver_name = config_observatory.values.weather_driver
    if weather_driver_name == "weather_winer":
        from .drivers import weather_winer
        weather = weather_winer
        weather.initialize()
    else:
        raise Exception("Unrecognized weather driver: %s" % weather_driver_name)

    weather_thread.start(weather)

def get_site_now():
    """
    Return a PyEphem Observer instance using the configured latitude and longitude,
    with the date set to the current time
    """

    site = ephem.Observer()
    site.lat = math.radians(config_observatory.values.latitude_degs)
    site.lon = math.radians(config_observatory.values.longitude_degs)
    site.date = ephem.now()    

    return site

def get_sun_altitude_degs():
    """
    Get the current sun elevation at the configured site latitude/longitude
    """
    site = get_site_now()
    sun = ephem.Sun()
    sun.compute(site)

    return math.degrees(sun.alt)

def get_filter_by_prefix(prefix):
    """
    Given a single letter prefix, return a tuple:
      (first_index, is_unique, names)

    first_index is the integer index of the first filter beginning
    with "prefix" in the filter list (case sensitive), or -1 if 
    no such filter is found.

    is_unique will be True if there is only one filter matching the
    criteria, or False if more than one filter matches.

    names is a list of all filter names matching the prefix
    """

    names = []
    indices = []
    for i, filter_name in enumerate(camera.get_filter_names()):
        if filter_name.startswith(prefix):
            names.append(filter_name)
            indices.append(i)

    if len(indices) == 0:
        return (-1, False, names)
    elif len(indices) == 1:
        return (indices[0], True, names)
    else:
        return (indices[0], False, names)

def get_relative_focus_offset(current_filter_index, next_filter_index):
    """
    Assuming we are currently in focus for current_filter_index, return
    how far we need to offset the focus position to be in focus for
    next_filter_index.
    """

    # Re-read the config file in case anything has changed
    config_focus_offsets.read()

    current_filter_focus = config_focus_offsets.values.best_focus_value.get(current_filter_index, None)
    next_filter_focus = config_focus_offsets.values.best_focus_value.get(next_filter_index, None)

    logging.info("current_filter_index = %s", current_filter_index)
    logging.info("next_filter_index = %s", next_filter_index)
    logging.info("current_filter_focus = %s", current_filter_focus)
    logging.info("next_filter_focus = %s", next_filter_focus)

    if current_filter_focus is None or next_filter_focus is None:
        # Not enough information to produce a usable offset.
        # Just keep the same focus position
        return 0
    else:
        # Return the relative offset between the two focus positions
        return next_filter_focus - current_filter_focus
        
def set_filter_and_offset_focuser(filter_prefix_or_index):
    """
    Move the filter wheel to the specified filter, and offset
    the focuser by the appropriate amount based on focus_offsets.cfg

    If filter_prefix_or_index is an integer, it is treated as a
    (zero-based) index of the desired filter position.

    If filter_prefix_or_index is a string, it is treated as a prefix
    of the desired filter name, and the index will be determined from
    the list of filter names.
    """

    filter_names = camera.get_filter_names()

    current_filter_index = camera.get_active_filter()
    current_filter_name = filter_names[current_filter_index]

    if type(filter_prefix_or_index) == int:
        next_filter_index = filter_prefix_or_index
    else:
        (next_filter_index, is_unique, matching_filter_names) = get_filter_by_prefix(filter_prefix_or_index)
    
    next_filter_name = filter_names[next_filter_index]

    logging.info("Moving from filter index %d (%s) to filter index %d (%s)", 
            current_filter_index, 
            current_filter_name,
            next_filter_index,
            next_filter_name
            )

    # HACK - for unknown reasons, after an autofocus run, setting a new filter
    # and later querying the current filter will return the old filter position.
    # This could lead to double focus offsets being applied to filters. Repeatedly
    # try changing filters until we read back that the new filter has been set

    filter_condition = False
    while not filter_condition:
        logging.info("Setting filter")
        camera.set_active_filter(next_filter_index)
        active_filter = camera.get_active_filter()
        logging.info("Expect filter = %d, got filter = %d",
                next_filter_index,
                active_filter)
        filter_condition = (active_filter == next_filter_index)
        

    focus_offset = get_relative_focus_offset(current_filter_index, next_filter_index)
    if focus_offset == 0:
        logging.info("Keeping focuser at same position")
    else:
        focus_target = focuser.Position + focus_offset
        if focus_target > 30000: #Current grism has a large offset that could go beyond travel of focuser.
            focus_target = 30000
        elif focus_target < 0:
            focus_target = 0
        logging.info("Offsetting focuser from %f by %f", focuser.Position, focus_offset)
        move_focuser(focus_target)

def move_focuser(focus_target):
    """
    Begin moving the focuser to the target position.
    Monitor the movement until the focuser stops.
    Make sure that we don't wait indefinitely, and check
    to see if focuser arrived at the correct position.
    """

    logging.info("Focuser moving to position %f", focus_target)

    starting_position = focuser.Position

    start_time = time.time()
    focuser.Move(focus_target)
    while focuser.IsMoving:
        if time.time() - start_time > config_observatory.max_focuser_move_time_seconds:
            logging.warn("Focuser has taken longer than %f seconds to move from %f to %f. Currently at %f. Aborting move.",
                    config_observatory.max_focuser_move_time_seconds,
                    starting_position,
                    focus_target,
                    focuser.Position)
            comhelper.callmethod(focuser.Halt)
            return False
        time.sleep(0.2)

    logging.info("Focuser is now at position %f", focuser.Position)

    # Did we arrive at the correct position?
    if abs(focuser.Position - focus_target) > config_observatory.max_focuser_error_counts:
        logging.warn("Focuser stopped at position %f, which is more than %f counts from target position %f",
                focuser.Position,
                config_observatory.max_focuser_error_counts,
                focus_target)

        return False

    return True  # Looks like everything worked correctly


def get_latest_weather():
    """
    Get a copy of the latest WeatherReading read from the weather_thread.
    May return None if weather has not been updated yet.
    """

    return weather_thread.get_latest_weather()

def observing_night_date():
    """
    Return a datetime.date instance representing the date of the current
    "observing night", which is what the date was in the local timezone
    when the observing night began. 

    For example, if the night begins at 5pm on 12/24/2015 and ends at 6am
    on 12/25/2015, this function would return a date object corresponding
    to 12/24/2015 if called at any time during the night of observations.

    The observing day increments at noon local time.

    NOTE: This function assumes that the computer's timezone is set for
    the location of the observatory - i.e. that datetime.now() returns
    the actual local time at the observatory.
    """

    return (datetime.datetime.now() - datetime.timedelta(hours=12)).date()


