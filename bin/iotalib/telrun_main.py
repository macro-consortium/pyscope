"""
Main telrun script. Called from telrun.py, which catches any
errors we may throw and attempts to send e-mail notification.
"""

import logging
import math
import os
import time

from win32com.client import Dispatch

# iotalib imports
from . import convert
from . import config_observatory
from . import config_notification
from . import consoleutil
from . import observatory
from . import paths
from . import telrunfile

def run():
    logging.info("STARTING TELRUN")

    config_observatory.read()
    #consoleutil.resize_console_window(100, 50)

    observatory.setup_camera()
    observatory.setup_mount()

    logging.info("Sun altitude: %.3f degrees", observatory.get_sun_altitude_degs())

    logging.info("Loading telrun.sls")
    telrun_file = telrunfile.TelrunFile("../schedules/telrun.sls") # TODO: Locate schedule using the paths module

    # Do basic sanity checks on telrun scans
    missing_filters = {}  # Dictionary where key is each unique missing filter name, and value is 1
    ambiguous_filters = {} # Dictionary where key is each ambiguous filter name, and value is a list of possible matching filters
    for scan in telrun_file.scans:
        logging.info("Checking scan with EDB line: %s" % scan.raw_edb)
        
        if (scan.sx < 0 or 
            scan.sx + scan.sw > observatory.camera.CameraXSize or
            scan.sy < 0 or
            scan.sy + scan.sh > observatory.camera.CameraYSize
            ):
            logging.warn("Scan image geometry %dx%d+%d+%d out of bounds for current camera. Will take a full-frame image (%d x %d)",
                    scan.sw,
                    scan.sh,
                    scan.sx,
                    scan.sy,
                    observatory.camera.CameraXSize,
                    observatory.camera.CameraYSize)
            scan.sx = 0
            scan.sy = 0
            scan.sw = observatory.camera.CameraXSize
            scan.sh = observatory.camera.CameraYSize

        fail_scan = False

        # Check if filter is OK
        (filter_index, is_unique, matching_filter_names) = observatory.get_filter_by_prefix(scan.filter)
        if filter_index == -1:
            missing_filters[scan.filter] = 1
            fail_scan = True
        elif is_unique == False:
            ambiguous_filters[scan.filter] = matching_filter_names
            fail_scan = True

        if fail_scan:
            logging.warn("Skipping scan due to invalid filter '%s'...",
                    scan.filter)
            scan.status = telrunfile.STATUS_FAIL
            ## TODO: mark scan as failed in telrun file

    if len(missing_filters) > 0 or len(ambiguous_filters) > 0:
        logging.warn("THERE WERE PROBLEMS WITH THE FILTERS SPECIFIED IN THE TELRUN FILE!!")
        if len(missing_filters) > 0:
            logging.warn("The following filter prefixes could not be found in Maxim:")
            for filter_prefix in list(missing_filters.keys()):
                logging.warn("  %s", filter_prefix)
        if len(ambiguous_filters) > 0:
            logging.warn("The following filter prefixes are ambiguous:")
            for filter_prefix, matching_filter_names in list(ambiguous_filters.items()):
                logging.warn("  %s (matches: %s)",
                        filter_prefix,
                        ", ".join(matching_filter_names))

        logging.warn("Any scan using these filters will be SKIPPED")
        logging.warn("Press Ctrl-C to abort this run and fix the telrun.sls file")
        logging.warn("or your Maxim config")
        logging.warn("Pausing for 10 seconds...")
        time.sleep(10)



    for scan in telrun_file.scans:
        logging.info("Processing scan:")
        logging.info(scan)

        if scan.status != telrunfile.STATUS_NEW:
            logging.info("Skipping scan with status = %s", scan.status)
            continue


        # TODO: Wait until time.time() > scan.starttm
        # Verify whether starttm is in local or UTC time

        scan.obj.compute(observatory.get_site_now())
        if math.degrees(scan.obj.alt) < config_observatory.values.min_telescope_altitude_degs:
            logging.warn("Skipping scan; altitude %s below telescope limit", scan.obj.alt)
            # TODO: Mark scan as failed in telrun file
            continue
        ########CHECK AZIMUTH###################
        if math.degrees(scan.obj.az) <= 5.0 or math.degrees(scan.obj.az) >= 355.0:
            logging.warn("Skipping scan; azimuth between 355 and 5 degrees")
            # TODO: Mark scan as failed in telrun file
            continue
        ########################################
        
        logging.info("EDB line: %s" % scan.raw_edb)
        logging.info("Object a_ra, a_dec: %s, %s" % (
            convert.to_dms(convert.rads_to_hours(scan.obj.a_ra)),
            convert.to_dms(convert.rads_to_degs(scan.obj.a_dec))
            ))
        logging.info("Object g_ra, g_dec: %s, %s" % (
            convert.to_dms(convert.rads_to_hours(scan.obj.g_ra)),
            convert.to_dms(convert.rads_to_degs(scan.obj.g_dec))
            ))
        logging.info("Object ra, dec: %s, %s" % (
            convert.to_dms(convert.rads_to_hours(scan.obj.ra)),
            convert.to_dms(convert.rads_to_degs(scan.obj.dec))
            ))
        
        # Hack: Change ra,dec to g_ra, g_dec to avoid topocentric coord error RLM 6Dec19 (fix later) 
        ra_app_hours = convert.rads_to_hours(scan.obj.g_ra)
        dec_app_degs = convert.rads_to_degs(scan.obj.g_dec)

        (ra_j2000_hours, dec_j2000_degs) = convert.jnow_to_j2000(ra_app_hours, dec_app_degs)

        logging.info("Slewing to J2000 RA %s, Dec %s", 
                convert.to_dms(ra_j2000_hours),
                convert.to_dms(dec_j2000_degs)
                )

        # This call will block until slew is complete
        # TODO: make these actions work in parallel
        observatory.mount.SlewToCoordinates(ra_app_hours, dec_app_degs)

        tele_ra_app_hours = observatory.mount.RightAscension
        tele_dec_app_degs = observatory.mount.Declination

        (tele_ra_j2000_hours, tele_dec_j2000_degs) = convert.jnow_to_j2000(tele_ra_app_hours, tele_dec_app_degs)

        logging.info("Arrived at J2000 RA %s, Dec %s",
                convert.to_dms(tele_ra_j2000_hours),
                convert.to_dms(tele_dec_j2000_degs)
                )

        logging.info("Settling for %d seconds", config_observatory.values.settle_time_secs)
        time.sleep(config_observatory.values.settle_time_secs)

        (filter_index, is_unique, matching_filter_names) = observatory.get_filter_by_prefix(scan.filter)
        logging.info("Setting filter to '%s' (index %d)", scan.filter, filter_index)
        observatory.camera.Filter = filter_index

        # TODO: Are subframes specified in binned or native pixel coordinateS?

        logging.info("Setting subframe to %dx%d starting at x=%d, y=%d, binning %dx%d",
                scan.sw,
                scan.sh,
                scan.sx,
                scan.sy,
                scan.binx,
                scan.biny
                )

        observatory.camera.BinX = scan.binx
        observatory.camera.BinY = scan.biny
        observatory.camera.StartX = scan.sx
        observatory.camera.StartY = scan.sy
        observatory.camera.NumX = scan.sw
        observatory.camera.NumY = scan.sh


        if scan.shutter == telrunfile.CCDSO_OPEN:
            shutter_state = 1
        elif scan.shutter == telrunfile.CCDSO_CLOSED:
            shutter_state = 0
        else:
            logging.warn("Unsupported shutter mode '%s'; skipping...", scan.shutter)
            # TODO: mark scan as failed
            continue
            
        logging.info("Starting %.3f second exposure",
                scan.dur)
        observatory.camera.Expose(scan.dur, shutter_state)

        logging.info("Waiting for image...")
        while not observatory.camera.ImageReady:
            time.sleep(0.1)

        # TODO: Add custom FITS headers

        image_file_path = os.path.abspath(os.path.join(paths.image_dir(), scan.imagefn))
        image_file_dir = os.path.dirname(image_file_path)
        logging.info("Saving to %s", image_file_path)
        if not os.path.isdir(image_file_dir):
            logging.info("Image directory %s does not exist. Creating...", image_file_dir)
            os.makedirs(image_file_dir)
        observatory.camera.SaveImage(image_file_path)
        logging.info("Saved!")




    
if __name__ == "__main__":
    print("Please run this from the telrun.py wrapper script")

