import logging
import math

import ephem
from win32com.client import Dispatch

from . import config_observatory

maxim = None   # Reference to MaxIm.Application object
camera = None  # Reference to MaxIm.CCDCamera object
mount = None   # Reference to ASCOM Telescope object
dome_monitor = None  # TODO

def setup_camera():
    global maxim
    global camera

    logging.info("Launching MaxIm.Application")
    maxim = Dispatch("MaxIm.Application")
    maxim.LockApp = True # Prevent Maxim from closing on application exit

    logging.info("Launching MaxIm.CCDCamera")
    camera = Dispatch("MaxIm.CCDCamera")
    camera.DisableAutoShutdown = True # Prevent camera from disconnecting on application exit

    logging.info("Connecting to camera")
    camera.LinkEnabled = True
    logging.info("Connected to camera '%s'", camera.CameraName)
    logging.info("Filters:")
    for i in range(len(camera.FilterNames)):
        logging.info(" %d: %s", i, camera.FilterNames[i])


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

def get_site_now():
    site = ephem.Observer()
    site.lat = math.radians(config_observatory.values.latitude_degs)
    site.lon = math.radians(config_observatory.values.longitude_degs)
    site.date = ephem.now()    

    return site

def get_sun_altitude_degs():
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
    for i, filter_name in enumerate(camera.FilterNames):
        if filter_name.startswith(prefix):
            names.append(filter_name)
            indices.append(i)

    if len(indices) == 0:
        return (-1, False, names)
    elif len(indices) == 1:
        return (indices[0], True, names)
    else:
        return (indices[0], False, names)
        
