"""
Main telrun script. Called from telrun.py, which catches any
errors we may throw and attempts to send e-mail notification.
"""

# Built-in Python imports
import atexit
import logging
import math
import os
import shutil
import signal
import sys
import time

# Third-party imports
import ephem
from astropy.io import fits as pyfits
from win32com.client import Dispatch
import numpy as np
from astroquery.jplhorizons import Horizons
from astropy import units as u
from astropy.coordinates import Angle


# iotalib imports
from . import airmass
from . import center_target_pinpoint
from . import comhelper
from . import convert
from . import config_focus_offsets
from . import config_observatory
from . import config_telrun
from . import config_wcs
from . import consoleutil
from . import email_warnings_thread
from . import observatory
from . import paths
from . import telrunfile
from . import telrun_gui
from . import telrun_status
from . import check_roof

def read_configs():
    config_observatory.read()
    config_focus_offsets.read()
    config_telrun.read()
    config_wcs.read()

def setup_observatory_connections():
    telrun_status.camera_state = "Connecting"
    observatory.setup_camera()
    telrun_status.camera_state = "Connected"

    telrun_status.mount_state = "Connecting"
    observatory.setup_mount()
    telrun_status.mount_state = "Connected"

    observatory.setup_focuser()

    telrun_status.autofocus_state = "Connecting"
    observatory.setup_autofocus()
    telrun_status.autofocus_state = "Connected"

    observatory.setup_weather()


def exit_handler():
    """
    Try to perform some cleanup on program exit
    """

    logging.info("Stopping any in-progress slews")
    try:
        comhelper.callmethod(observatory.mount.AbortSlew)
    except Exception as ex:
        logging.exception("Error aborting slew during shutdown")

    logging.info("Attempting to turn off tracking...")
    try:
        observatory.mount.Tracking = False
    except Exception as ex:
        logging.exception("Error turning off tracking during shutdown")

    logging.info("Attempting to abort autofocus (if needed)...")
    try:
        observatory.autofocus.abort_autofocus()
    except:
        logging.exception("Error aborting autofocus during shutdown")

    logging.info("Attempting to abort any in-progress camera exposures...")
    try:
        observatory.camera.abort_exposure()
    except:
        logging.exception("Error aborting exposure during shutdown")

    logging.info("Attempting to stop focuser...")
    try:
        comhelper.callmethod(observatory.focuser.Halt)
    except:
        logging.exception("Error stopping focuser during shutdown")

def run():
    # email_warnings_thread.start()   -- 6/21/21 WWG - TODO: fix permissions problems

    telrun_gui.start_gui_in_thread()

    logging.info("STARTING TELRUN")

    read_configs()
    setup_observatory_connections()

    # Catch Ctrl-C and crashes, and try to perform some cleanup 
    # (like turning off tracking, aborting exposures, etc).
    # Now that we've connected to all devices, we should be able
    # to accomplish this...
    atexit.register(exit_handler)

    # Give telrun_status access to our sun elevation calculation function
    # now that things like latitude and longitude have (hopefully) been
    # loaded from the mount
    telrun_status.sun_elevation_func = observatory.get_sun_altitude_degs
    telrun_status.get_weather_func = observatory.get_latest_weather

    # Get the camera cooler going...
    logging.info("Setting camera cooler setpoint to %.1f C", config_telrun.values.camera_cooler_celsius)
    observatory.camera.set_ccd_temperature_setpoint_celsius(config_telrun.values.camera_cooler_celsius)

    # Home the mount if needed
    if config_telrun.values.home_mount_at_start:
        logging.info("Homing mount")
        try:
            homefunc = observatory.mount.FindHome
            if hasattr(homefunc, '__call__'):
                homefunc()
        except:
            logging.exception("Unable to home mount")

    # Wait for CCD temperature regulation
    logging.info("Waiting for CCD to reach setpoint")
    cooler_warning_sent = False
    cooler_start_time = time.time()
    while True:
        ccd_temperature_celsius = observatory.camera.get_ccd_temperature_celsius()
        temp_error = abs(config_telrun.values.camera_cooler_celsius - ccd_temperature_celsius)
        logging.info("CCD: %.1f C, Target: %.1f C, Delta: %.1f C, Tolerance: %.1f C",
                ccd_temperature_celsius,
                config_telrun.values.camera_cooler_celsius,
                temp_error,
                config_telrun.values.camera_cooler_tolerance
                )

        if temp_error < config_telrun.values.camera_cooler_tolerance:
            logging.info("CCD temperature close enough to setpoint. Continuing with run...")
            break

        if not cooler_warning_sent and time.time() - cooler_start_time > config_telrun.values.camera_cooler_warning_minutes*60:
            logging.warn("CCD has not cooled to setpoint %f C after %f minutes. Currently at %f C",
                    config_telrun.values.camera_cooler_celsius,
                    config_telrun.values.camera_cooler_warning_minutes,
                    ccd_temperature_celsius
                    )
            cooler_warning_sent = True

        time.sleep(10)

    # From this point on everything should be set up, and we can hopefully operate
    # indefinitely (or until something goes wrong)
    while True:
        logging.info("Starting main_operation_loop...")
        main_operation_loop()

def deg2sex(eph):
    ra = Angle(np.array(eph['RA'])[0], u.degree)
    ra_str = ra.to_string(unit=u.hour, sep=':',precision=2)
    dec = Angle(np.array(eph['DEC'])[0], u.degree)
    dec_str = dec.to_string(unit=u.degree, sep=':',precision =1)
    ra_rate = np.array(eph['RA_rate'].to('arcsec/s'))[0]
    dec_rate = np.array(eph['DEC_rate'].to('arcsec/s'))[0]
    return ra_str,dec_str, ra_rate, dec_rate

def query_jpl(object_id, id_type = None):
    #Queries jpl horizon site and returns object if successful
    if id_type == None:
        obj = Horizons(id = object_id, id_type = 'smallbody', location = '857')
    else:
        obj = Horizons(id = object_id, id_type = id_type, location = '857')
    try:
        eph = obj.ephemerides()
        return eph
    except:
        #print(obj.ephemerides())
        return None
    



# Keep track of the file modification time for any 
# telrun.sls files that we get all the way through, so
# that we don't try to reload the same file on the next
# pass through this loop
completed_telrun_file_modification_time = 0

def main_operation_loop():
    global completed_telrun_file_modification_time

    telrun_new_path = paths.telrun_sls_path("telrun.new")
    telrun_sls_path = paths.telrun_sls_path("telrun.sls")
    
    telrun_file = None
    # If telrun.sls exists, start out by loading it. We might replace
    # it with telrun.new later
    if os.path.isfile(telrun_sls_path) and os.path.getmtime(telrun_sls_path) != completed_telrun_file_modification_time:
        logging.info("Loading existing telrun.sls")
        telrun_file = telrunfile.TelrunFile(telrun_sls_path)
        check_telrun_file(telrun_file)

    while True:
        if os.path.isfile(telrun_new_path):
            logging.info("Found telrun.new; renaming to telrun.sls")
            shutil.move(telrun_new_path, telrun_sls_path)
            logging.info("Loading telrun.sls")
            telrun_file = telrunfile.TelrunFile(telrun_sls_path)
            check_telrun_file(telrun_file)

        if telrun_file is None:
            logging.debug("No active telrun file; sleeping...")
            time.sleep(5)
            continue            
        sun_alt_degs = observatory.get_sun_altitude_degs()
        if config_telrun.values.check_roof_value:
            while True:
                try:
                    if check_roof.checkOpen() == True:
                        logging.info("Roof is open")
                        break
                    else:
                        logging.info("Roof is not open, waiting...")
                except Exception as ex:
                        logging.exception("Error refreshing roof info")
                time.sleep(60)
        if not config_telrun.values.wait_for_sun \
            or sun_alt_degs < config_observatory.max_sun_altitude_degs:
            logging.info("Sun altitude: %.3f (below limit; starting scans)", sun_alt_degs)
            telrun_file_finished = run_scans(telrun_file)
            if telrun_file_finished:
                completed_telrun_file_modification_time = os.path.getmtime(telrun_sls_path)
                logging.info("FINISHED processing telrun.sls with file modification time %s", completed_telrun_file_modification_time)


            logging.info("Moving telescope to stow position: azimuth=%f degs, altitude=%f degs",
                config_observatory.stow_azimuth_degs,
                config_observatory.stow_altitude_degs)

            observatory.mount.SlewToAltAz(config_observatory.stow_azimuth_degs, config_observatory.stow_altitude_degs)
            logging.info("Turning tracking off")
            observatory.mount.Tracking = False
            logging.info("Telescope arrived at azimuth = %f, altitude = %f",
                observatory.mount.Azimuth,
                observatory.mount.Altitude)

            logging.info("EXITING MAIN OPERATION LOOP")
            return
        else:
            logging.info("Sun altitude: %.3f degs (above limit of %s)", 
                    sun_alt_degs,
                    config_observatory.max_sun_altitude_degs)
            time.sleep(10)

def check_telrun_file(telrun_file):
    logging.info("Performing sanity checks on telrun.sls file...")

    unique_filenames = {} # Dictionary where key is unique filename and value is 1
    for scan in telrun_file.scans:
        if scan.imagefn in unique_filenames:
            logging.warn("Duplicate filename in telrun file: %s", scan.imagefn)
        unique_filenames[scan.imagefn] = 1


    missing_filters = {}  # Dictionary where key is each unique missing filter name, and value is 1
    ambiguous_filters = {} # Dictionary where key is each ambiguous filter name, and value is a list of possible matching filters
    for scan in telrun_file.scans:
        logging.info("Checking scan with EDB line: %s" % scan.raw_edb)
        camera_width = observatory.camera.get_ccd_width_pixels()
        camera_height = observatory.camera.get_ccd_height_pixels()

        if (scan.sx < 0 or 
            scan.sx + scan.sw > camera_width or
            scan.sy < 0 or
            scan.sy + scan.sh > camera_height 
            ):
            logging.warn("Scan image geometry %dx%d+%d+%d out of bounds for current camera. Will take a full-frame image (%d x %d)",
                    scan.sw,
                    scan.sh,
                    scan.sx,
                    scan.sy,
                    camera_width,
                    camera_height)
            scan.sx = 0
            scan.sy = 0
            scan.sw = camera_width
            scan.sh = camera_height

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
        logging.warn("You may need to fix the telrun.sls file or your Maxim DL filter listing")
        logging.info("Pausing for 10 seconds...")
        time.sleep(10)

def run_scans(telrun_file):
    """
    Iterate through the scans in a telrun file.
    Return True if the telrun file was completely processed,
    or False if scans were interrupted for some other reason (such as the sun coming up)
    """

    # Keep track of how long it's been since we've attempted to do an autofocus run
    if config_telrun.values.autofocus_interval_seconds > 0:
        do_periodic_autofocus = True
    else:
        do_periodic_autofocus = False

    if config_telrun.values.autofocus_before_first_observation:
        next_autofocus_time = 0 # Run autofocus at the first opportunity
    else:
        next_autofocus_time = time.time() + config_telrun.values.autofocus_interval_seconds


    num_scans = len(telrun_file.scans)
    telrun_status.total_scan_count = num_scans

    for scan_index in range(num_scans):
        scan = telrun_file.scans[scan_index]

        telrun_status.current_scan_number = scan_index+1
        telrun_status.current_scan = scan
        if scan_index < num_scans-1:
            telrun_status.next_scan = telrun_file.scans[scan_index+1]
        else:
            telrun_status.next_scan = None
        telrun_status.next_autofocus_time = next_autofocus_time
        sun_alt_degs = observatory.get_sun_altitude_degs()
        logging.info("Sun altitude: %.3f degrees", sun_alt_degs)
        if config_telrun.values.wait_for_sun and sun_alt_degs > config_observatory.max_sun_altitude_degs:
            logging.info("Sun is above limit of %s. Stopping...", config_observatory.max_sun_altitude_degs)
            return False

        logging.info("Processing scan %d of %d:", scan_index+1, num_scans)
        logging.info(scan)
        logging.info("EDB line: %s" % scan.raw_edb)

        if scan.status != telrunfile.STATUS_NEW:
            logging.info("Skipping scan with status = %s", scan.status)
            telrun_status.skipped_scan_count += 1
            continue
        
        seconds_until_starttm = scan.starttm - time.time()
        if seconds_until_starttm < config_telrun.values.seconds_until_starttm:
            logging.info("Skipping scan %.2f seconds late, exceeding late limit", abs(seconds_until_starttm))
            telrun_status.skipped_scan_count += 1
            continue
        
        while True:
            if seconds_until_starttm < 0:
                logging.info("%.2f seconds late starting scan", abs(seconds_until_starttm))
            
            # TODO: slew to scan early, and wait until starttm to begin exposure
            logging.info("Waiting %.2f seconds (%.3f hours) to start scan",
                seconds_until_starttm,
                seconds_until_starttm/3600.0)
            if not config_telrun.values.wait_for_scan_start_time:
                logging.info("(not actually waiting based on config)")
            elif seconds_until_starttm > 0: time.sleep(seconds_until_starttm)
            
        # TODO: Check for lstdelta
            logging.info("scan.startdt = %s", scan.startdt)

            scan.obj.compute(observatory.get_site_now())
            if math.degrees(scan.obj.alt) < config_observatory.values.min_telescope_altitude_degs:
                logging.warn("Skipping scan %s (%s); altitude %s below telescope limit", 
                    scan.title,
                    scan.observer,
                    scan.obj.alt)
                telrun_status.skipped_scan_count += 1

                set_scan_status(telrun_file, scan, "F")

                break
        
            try:
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
            except:
                logging.info("Error while logging debug coordinates. Continuing...")
            
        # Changed .ra, .dec to .g_ra, .g_dec RLM 13 Dec 19 (ephem problem)
            target_ra_app_hours = convert.rads_to_hours(scan.obj.g_ra)
            target_dec_app_degs = convert.rads_to_degs(scan.obj.g_dec)

            (target_ra_j2000_hours, target_dec_j2000_degs) = convert.jnow_to_j2000(target_ra_app_hours, target_dec_app_degs)
            
            centering_result=False
            if config_telrun.values.recenter_if_returns_true(scan):
                filter_index = config_telrun.values.autofocus_filter_index
                logging.info("Switching to filter %s for recentering adjustment", filter_index)
                observatory.set_filter_and_offset_focuser(filter_index)

                telrun_status.mount_state = "SLEWING"
                
                if scan.posx is not None and scan.posy is not None:
                    logging.info("Refining telescope pointing for this scan...")
                    centering_result = center_target_pinpoint.center_coordinates_on_pixel(target_ra_j2k_hrs=target_ra_j2000_hours, 
                            target_dec_j2k_deg=target_dec_j2000_degs, 
                            target_pixel_x_unbinned=scan.posx, 
                            target_pixel_y_unbinned=scan.posy, 
                            initial_offset_dec_arcmin=0, 
                            check_and_refine=True,
                            max_attempts=5, 
                            tolerance_pixels=1, 
                            exposure_length=config_telrun.values.recenter_exposure_seconds,
                            binning=config_telrun.values.recenter_exposure_binning, 
                            save_images=True, 
                            save_path_template=r'{MyDocuments}\CenterTargetData\{Timestamp}', 
                            console_output=False,
                            search_radius_degs=1, 
                            sync_mount=config_telrun.values.recenter_using_sync)
                
                if not centering_result:
                    logging.info("Recentering failed. Continuing...")
                else:
                    logging.info("Recentering succeeded. Continuing...")
            else:
                # Normal blind slew
                logging.info("Slewing to J2000 RA %s, Dec %s", 
                        convert.to_dms(target_ra_j2000_hours),
                        convert.to_dms(target_dec_j2000_degs)
                        )

                # This call will block until slew is complete
                # TODO: make these actions work in parallel
                telrun_status.mount_state = "SLEWING"
                # Check for lunar tracking in object comments and switch to lunar rate
                observatory.mount.Tracking = True
                if scan.comment == "LUNARTRACKINGRATE":
                    observatory.mount.TrackingRate = 1
                    logging.info("Switching to Lunar Tracking Rate")
                elif scan.comment.lower() == "nonsidereal":            
                    if scan.obj.name.upper() == 'MOON':
                        object_data = query_jpl('301',id_type='majorbody')
                    else:
                        object_data = query_jpl(scan.obj.name)
                    if object_data == None:
                        logging.info("JPL Horizons lookup failed for object name %s" % scan.obj.name)
                    else:
                        logging.info("JPL Horizons lookup successful. Calculated offset rate for %s", scan.obj.name)
                        ra_str, dec_str, ra_rate,dec_rate = deg2sex(object_data)
                        target_ra_j2000_hours = convert.from_dms(ra_str)
                        target_dec_j2000_degs = convert.from_dms(dec_str)
                        (target_ra_app_hours, target_dec_app_degs) = convert.j2000_to_jnow(target_ra_j2000_hours, target_dec_j2000_degs)
                        
                observatory.mount.SlewToCoordinatesAsync(target_ra_app_hours, target_dec_app_degs)
                while observatory.mount.Slewing:
                    time.sleep(0.2)

                telrun_status.mount_state = "SETTLING"

                logging.info("Settling for %d seconds", config_observatory.values.settle_time_secs)
                time.sleep(config_observatory.values.settle_time_secs)
                
                if scan.comment.lower() == 'nonsidereal':
                    if object_data == None:
                        continue
                    else:
                        observatory.mount.RightAscensionRate = ra_rate * 0.9972695677 / 15.041 * (1/np.cos(np.deg2rad(convert.from_dms(dec_str)))) 
                        observatory.mount.DeclinationRate =  dec_rate 
                        logging.info("Switching to Non-Sidereal Tracking Rates")
                        logging.info("Rates = (%.4f, %.4f) arcsec/sec" % (observatory.mount.RightAscensionRate, observatory.mount.DeclinationRate))

            tele_ra_app_hours = observatory.mount.RightAscension
            tele_dec_app_degs = observatory.mount.Declination

            (tele_ra_j2000_hours, tele_dec_j2000_degs) = convert.jnow_to_j2000(tele_ra_app_hours, tele_dec_app_degs)

            logging.info("Arrived at J2000 RA %s, Dec %s",
                convert.to_dms(tele_ra_j2000_hours),
                convert.to_dms(tele_dec_j2000_degs)
                )

            telrun_status.mount_state = "Tracking"

            if do_periodic_autofocus and time.time() > next_autofocus_time:
                telrun_status.autofocus_state = "RUNNING"
                do_autofocus()
                logging.info("Autofocus Mount Elevation is %s degrees" % observatory.mount.Altitude)
                next_autofocus_time = time.time() + config_telrun.values.autofocus_interval_seconds
                telrun_status.next_autofocus_time = next_autofocus_time
                telrun_status.autofocus_state = "Idle"
                

            observatory.set_filter_and_offset_focuser(scan.filter)

            # TODO: Are subframes specified in binned or native pixel coordinates?

            logging.info("Setting subframe to %dx%d starting at x=%d, y=%d, binning %dx%d",
                    scan.sw,
                    scan.sh,
                    scan.sx,
                    scan.sy,
                    scan.binx,
                    scan.biny
                    )

            observatory.camera.set_binning(scan.binx, scan.biny)
            observatory.camera.set_subframe(scan.sx, scan.sy, scan.sw, scan.sh)
            
            cmosmodes = ['HDR', 'High', 'Low', 'Stackpro']
            logging.info("Setting CMOS readout mode to mode %i: %s" % (scan.cmosmode, cmosmodes[scan.cmosmode]))
            observatory.camera.set_cmosmode(scan.cmosmode)

            if scan.shutter == telrunfile.CCDSO_OPEN:
                shutter_state = 1
            elif scan.shutter == telrunfile.CCDSO_CLOSED:
                shutter_state = 0
            else:
                logging.warn("Unsupported shutter mode '%s'; skipping...", scan.shutter)
                set_scan_status(telrun_file, scan, "F")
                break

            # Record information that will later be inserted into FITS header
            start_exp_camera_temp = observatory.camera.get_ccd_temperature_celsius()
            start_exp_guider_camera_temp = observatory.camera.get_ccd_guider_temperature_celsius()
            start_exp_lst_hours = convert.rads_to_hours(observatory.get_site_now().sidereal_time())
            scan.obj.compute(observatory.get_site_now())
            start_exp_alt_degs = convert.rads_to_degs(scan.obj.alt)
            start_exp_azm_degs = convert.rads_to_degs(scan.obj.az)
            start_exp_ha_hours = start_exp_lst_hours - target_ra_app_hours
            if start_exp_ha_hours < -12:
                start_exp_ha_hours += 24
            if start_exp_ha_hours > 12:
                start_exp_ha_hours -= 24
            start_exp_airmass = airmass.compute_airmass(start_exp_alt_degs)
            start_exp_focuspos = observatory.focuser.Position
        
            moon = ephem.Moon()
            moon.compute(observatory.get_site_now())
            start_exp_moon_separation_degs = convert.rads_to_degs(ephem.separation((scan.obj.az, scan.obj.alt), (moon.az, moon.alt)))
            start_exp_moon_phase = moon.phase
            
            logging.info("Starting %.3f second exposure",
                    scan.dur)
            telrun_status.camera_state = "EXPOSING"
            observatory.camera.start_exposure(scan.dur, shutter_state)
            expected_exposure_end_time = time.time() + scan.dur

            logging.info("Waiting for image...")
            while not observatory.camera.is_exposure_finished():
                if time.time() - expected_exposure_end_time > config_telrun.values.camera_timeout_seconds:
                    raise Exception("Timed out waiting for exposure from camera. Make sure there are no File Open/Save windows open in Maxim DL.")

                time.sleep(0.5)
            telrun_status.camera_state = "Idle"

            # In some cases when the camera connection has failed, Maxim will not throw an
            # exception, but will simply immediately return that the exposure is finished.
            # If this is the case, we would end up just saving the same (last successful) image
            # over and over again.
            observatory.camera.verify_latest_exposure()
            
            # check if grism image, if not, run pinpoint solution
            logging.info("Attempting a plate solve via Pinpoint...")
            if (observatory.camera.get_filter_names()[observatory.camera.get_active_filter()] != '6'):
                observatory.camera.run_pinpoint()
                try:
                    while observatory.camera.pinpoint_status() == 3:
                        time.sleep(0.01)
                    if observatory.camera.pinpoint_status() == 2:
                        logging.info("Pinpoint solution found! Continuing...")
                    else:
                        logging.info("Pinpoint solution failed, continuing...")
                except Exception as exception:
                    logging.info("Pinpoint error: %s" % exception)
            
            #Store offset rates for adding to FITS Header before changing 
            RA_rate_offset = observatory.mount.RightAscensionRate / 0.9972695677 
            DEC_rate_offset = observatory.mount.DeclinationRate  
            #Check for alternative tracking rates in comment and switch back to sidereal
            if scan.comment == "LUNARTRACKINGRATE":
                observatory.mount.TrackingRate = 0
                logging.info("Switching to Sidereal Tracking Rate")
            elif scan.comment.lower() == "nonsidereal":
                observatory.mount.RightAscensionRate = 0
                observatory.mount.DeclinationRate = 0
                logging.info("Switching to Sidereal Tracking Rate")
            logging.info("Turning off telescope tracking")
            observatory.mount.Tracking = False

            image_file_path_final = os.path.abspath(os.path.join(paths.image_dir(), scan.imagefn))
            image_file_path_tmp = image_file_path_final + ".tmp" # Camera writes raw image to this file (before Talon-style headers have been added)
            #image_file_path_after_headers = image_file_path_final + ".after_headers" # FITS library writes modified image to this file (after Talon-style headers have been added)
            image_file_dir = os.path.dirname(image_file_path_final)

            if not os.path.isdir(image_file_dir):
                logging.info("Image directory %s does not exist. Creating...", image_file_dir)
                os.makedirs(image_file_dir)
            logging.info("Saving to %s", image_file_path_tmp)

            # Make sure file doesn't already exist. (Maxim may be OK with overwriting
            # existing files, but other camera drivers may not be)
            remove_file_if_needed(image_file_path_tmp)
            observatory.camera.save_image_as_fits(image_file_path_tmp)
            logging.info("Saved!")

            logging.info("Adding custom FITS headers...")

            # Calculate additional values to be used in FITS header

            cdelt1 = config_wcs.values.arcsec_per_pixel_unbinned / 3600.0 # Convert to degrees per pixel
            cdelt2 = cdelt1 # Assume X and Y scale is the same

            cdelt1 *= scan.binx # Scale to account for binning
            cdelt2 *= scan.biny

            # Get the signs correct
            if config_wcs.values.mirrored:
                cdelt1 = -cdelt1 
            else:
                cdelt1 = -cdelt1
                cdelt2 = -cdelt2

            weather_reading = observatory.get_latest_weather()
            wxtemp = -999
            wxpres = -999
            wxwndspd = -999
            wxwnddir = -999
            wxhumid = -999
            wxage = -999
            if weather_reading.wind_speed_kph is not None:
                wxwndspd = weather_reading.wind_speed_kph
            if weather_reading.wind_direction_degs_east_of_north is not None:
                wxwnddir = weather_reading.wind_direction_degs_east_of_north
            if weather_reading.temperature_celsius is not None:
                wxtemp = weather_reading.temperature_celsius
            if weather_reading.pressure_millibars is not None:
                wxpres = weather_reading.pressure_millibars
            if weather_reading.humidity_percent is not None:
                wxhumid = weather_reading.humidity_percent
            if weather_reading.age_seconds() is not None:
                wxage = weather_reading.age_seconds()


            hdulist = pyfits.open(image_file_path_tmp, mode="update")
            header = hdulist[0].header
            header.set("OBJECT", scan.obj.name, "Object name")
            header.set("TELESCOP", config_observatory.values.telescope_name, "Telescope used to acquire image")
            header.set("OBSERVER", scan.observer, "Investigator(s)")
            header.set("OFFSET1", scan.sx, "Camera upper left frame x") # TODO: Is this in binned or unbinned coordinates?
            header.set("OFFSET2", scan.sy, "Camera upper left frame y") # TODO: Is this in binned or unbinned coordinates?
            header.set("XFACTOR", scan.binx, "Camera x binning factor")
            header.set("YFACTOR", scan.biny, "Camera y binning factor")
            header.set("ORIGIN", config_observatory.values.origin, "")
            header["COMMENT"] = scan.title
            header.set("PRIORITY", scan.priority, "Scheduling priority")
            header.set("CDELT1", cdelt1, "RA step right, degrees/pixel")
            header.set("CDELT2", cdelt2, "Dec step down, degrees/pixel")
            header.set("RA", convert.to_dms(tele_ra_j2000_hours), "Nominal center J2000 RA")
            header.set("DEC", convert.to_dms(tele_dec_j2000_degs), "Nominal center J2000 Dec")
            header.set("RAEOD", convert.to_dms(tele_ra_app_hours), "Nominal center Apparent RA")
            header.set("DECEOD", convert.to_dms(tele_dec_app_degs), "Nominal center Apparent Dec")
            header.set("OBJRA", convert.to_dms(target_ra_j2000_hours), "Target center J2000 RA")
            header.set("OBJDEC", convert.to_dms(target_dec_j2000_degs), "Target center J2000 Dec")
            header.set("RARATE", RA_rate_offset, "Mount RA Offset arcsec/sec")
            header.set("DECRATE", DEC_rate_offset, "Mount DEC Offset arcsec/sec")
            header.set("EPOCH", 2000, "RA/Dec epoch, years (obsolete)")
            header.set("EQUINOX", 2000, "RA/Dec equinox, years")
            header.set("LATITUDE", convert.to_dms(config_observatory.values.latitude_degs), "Site Latitude, degrees +N")
            header.set("LONGITUD", convert.to_dms(config_observatory.values.longitude_degs), "Site Longitude, degrees +E")
            header.set("ELEVATIO", convert.to_dms(start_exp_alt_degs), "Degrees above horizon")
            header.set("AZIMUTH", convert.to_dms(start_exp_azm_degs), "Degrees E of N")
            header.set("HA", convert.to_dms(start_exp_ha_hours), "Local Hour Angle")
            header.set("AIRMASS", start_exp_airmass, "Kasten-Young airmass computation")
            header.set("MOONANGL", start_exp_moon_separation_degs, "Angular separation to Moon, Degrees")
            header.set("MOONPHAS", start_exp_moon_phase, "Percentage of full moon")
            header.set("LST", convert.to_dms(start_exp_lst_hours), "Local sidereal time at exposure start")
            header.set("CAMTEMP", start_exp_camera_temp, "Camera temp, C")
            header.set("FOCUSPOS", start_exp_focuspos, "Focus position from home, um")
            header.set("WXTEMP", wxtemp, "Ambient air temp, C")
            header.set("WXPRES", wxpres, "Atm pressure, mB")
            header.set("WXWNDSPD", wxwndspd, "Wind speed, kph")
            header.set("WXWNDDIR", wxwnddir, "Wind dir, degs E of N")
            header.set("WXHUMID", wxhumid, "Outdoor humidity, percent")
            header.set("WXAGE", wxage, "Age of weather readings, seconds")
            header.set("CENTER", centering_result, "Result of recentering attempt")

            # Handle SSON custom headers
            if scan.ccdcalib.newc == telrunfile.CT_EXTCMD and scan.extcmd.startswith("fitsheader"):
                # sample extcmd:  "fitsheader USERNAME=DDJ"
                logging.info("Handling external command: '%s'" % scan.extcmd)
                fitsheader_args = scan.extcmd.split(" ")[1:]
                # Assume that there could potentially be several space-separated KW=VAL arguments given
                # and process all of them
                for fitsheader_arg in fitsheader_args:
                    kwval_fields = fitsheader_arg.split("=", 1)
                    if len(kwval_fields) == 2:
                        keyword = kwval_fields[0]
                        value = kwval_fields[1]
                        logging.info("Setting custom header '%s' = '%s'", keyword, value)
                        header.set(keyword, value, "")

            hdulist.flush()
            hdulist.close()

            # Move modified FITS file into final location, replacing any file
            # that may already be there. By writing to another file and then
            # renaming it at the last second, we make sure that other processed
            # (like the file transfer daemon) don't see incomplete, partially-written
            # files
            remove_file_if_needed(image_file_path_final)
            os.rename(image_file_path_tmp, image_file_path_final)
            logging.info("Final file saved to %s", image_file_path_final)

            set_scan_status(telrun_file, scan, "D")
            break
        continue

    observatory.camera.start_exposure(0.01, False) # Take a dark at the end of the night to close the shutter

    return True # Full telrun file has been processed
        

def remove_file_if_needed(filepath):
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as ex:
            logging.warn("Unable to remove file %s: %s", filepath, ex)

def do_autofocus():
    logging.info("Starting an autofocus run")

    filter_index = config_telrun.values.autofocus_filter_index
    logging.info("Switching to filter %s for focus run", filter_index)
    observatory.set_filter_and_offset_focuser(filter_index)

    if abs(observatory.focuser.Position - config_telrun.values.autofocus_starting_focus_position) > config_telrun.values.autofocus_starting_focus_position_tolerance:
        logging.warn("Focuser position %f is too far from nominal starting autofocus range %f +/- %f. Moving to %f for autofocus...",
                observatory.focuser.Position,
                config_telrun.values.autofocus_starting_focus_position,
                config_telrun.values.autofocus_starting_focus_position_tolerance,
                config_telrun.values.autofocus_starting_focus_position,
                )
        observatory.move_focuser(config_telrun.values.autofocus_starting_focus_position)

    exp_length_seconds = config_telrun.values.autofocus_exposure_length_seconds
    logging.info("Configuring autofocus run to use %s second exposures", exp_length_seconds)
    observatory.autofocus.set_exposure_length(exp_length_seconds)

    best_focus_result = observatory.autofocus.run_autofocus()

    if best_focus_result is None:
        logging.warn("Autofocus run failed to find best-focus solution. Sky may be cloudy or telescope may be too far out of focuser.")

    return best_focus_result

    
def set_scan_status(telrun_file, scan, code):
    if not config_telrun.values.update_sls_status_codes:
        logging.info("(not updating status code due to config)")
        return

    logging.info("Setting status code to '%s'", code)
    try:
        telrun_file.update_status_code(scan, code)
    except Exception as ex:
        logging.warn("Error updating telrun status code: %s", str(ex))

    
if __name__ == "__main__":
    print("Please run this from the telrun.py wrapper script")

