from datetime import datetime
import math
import os
import sys
import tempfile
import time
import astropy.io.fits as fits

from iotalib import convert
from iotalib import talonwcs
from iotalib import rst

import ephem
from win32com.client import Dispatch

"""
This script attempts to put a target RA and Dec at a particular pixel position
(which may be outside the bounds of the physical CCD in the case of an off-axis
spectrometer fiber).

The script slews to a target, takes an image, finds a WCS solution and offsets
the mount to place the target RA/Dec at the requested pixel position. This process
repeats until the target is positioned within a specified tolerance or the maximum
number of attempts has been exceeded.

The target pixel position can be calibrated by manually positioning a star at the
target position and running the calibrate_target_pixel script.
"""

### CONFIGURATION VALUES ########################

configuration_file = sys.argv[1]
config = []
with open(configuration_file) as infile:
    for line in infile:
        config.append((line.split()[0]))    

MOUNT_DRIVER = "ASCOM.SoftwareBisque.Telescope"  # Use this for the Paramount ME (controlled through TheSky)

OBJECT_NAME = ""                       # Provides the name of an object to search for in the SIMBAD Database (If empty string, use provided coordinates)
TARGET_RA_J2000_HOURS = sys.argv[2] # RA coordinates of the target star, in J2000 hours
TARGET_DEC_J2000_DEGS = sys.argv[3] # Dec coordinates of the target star, in J2000 degrees
TARGET_PIXEL_X_UNBINNED = float(config[4])        # Target X pixel position in unbinned image. Center of the top left corner pixel is (1, 1)
TARGET_PIXEL_Y_UNBINNED = float(config[5])       # Target Y pixel position in unbinned image. Center of the top left corner pixel is (1, 1)
TOLERANCE_PIXELS = float(config[7])                  # Continue refining pointing until target RA/Dec is within this many pixels of target pixel location
MAX_RESLEW_ATTEMPTS = int(config[8])                # Give up after trying to refine pointing this many times
INITIAL_OFFSET_DEC_ARCMIN = float(config[9])        # Offset for first image, to avoid blooming on bright target

SETTLE_TIME_SECONDS = float(config[10])               # Pause for this many seconds after slewing to each target before taking an image
EXPOSURE_LENGTH_SECONDS_CENTER = float(config[6])           # Exposure length of each image, in seconds
BINNING = float(config[11])                            # Image binning (higher binning reduces resolution but speeds up image readout time) 

ARCSEC_PER_PIXEL_UNBINNED = float(config[0])       # Estimated image scale of UNBINNED image, in arcseconds per pixel
MIRRORED = False                       # If image can be rotated so that North is Up and East is Right, this should be True to ensure that a WCS solution can be found.

SAVE_IMAGES = config[2]                     # If True, each image will be saved to SAVE_DATA_PATH
SAVE_DATA_PATH = r"{MyDocuments}\CenterTargetData\{Timestamp}" # Script data will be saved to this location.

VERBOSE_WCS_OUTPUT = config[1]             # If True, output from the WCS script will be shown on the console in realtime. Useful for diagnosing WCS problems.

### END CONFIGURATION VALUES ########################


def main():
    """
    Starting point for the center_target_on_pixel script
    """
    
    performed_initial_offset = False

    if OBJECT_NAME == "":
        target_ra_j2000_hours = convert.from_dms(TARGET_RA_J2000_HOURS)
        target_dec_j2000_degs = convert.from_dms(TARGET_DEC_J2000_DEGS)
    else:
        finder = rst.ObjectFinder()
        inCoords = finder.sesame_resolve(OBJECT_NAME)
        target_ra_j2000_hours = finder.hr2hms(inCoords[0])
        target_dec_j2000_degs = finder.deg2dms(inCoords[1])

    print("Launching mount control software...")
    mount = Dispatch(MOUNT_DRIVER)

    print("Connecting to mount...")
    mount.Connected = True

    print("Launching MaxIm DL...")
    maxim = Dispatch("MaxIm.Application")
    maxim.LockApp = True
    
    camera = Dispatch("MaxIm.CCDCamera")
    camera.DisableAutoShutdown = True

    print("Connecting to camera...")
    camera.LinkEnabled = True
    
    if mount.CanSetTracking:
        # Not all mount drivers support turning tracking on/off.
        # For example, the ASCOM driver for TheSky does not support it.
        # However, if it is supported, make sure tracking is on before slewing
        mount.Tracking = True
    
    save_data_path = parse_filepath_template(SAVE_DATA_PATH)
    
    if SAVE_IMAGES and not os.path.isdir(save_data_path):
        print("Creating directory '%s'" % save_data_path)
        os.makedirs(save_data_path)
    

    slew_ra_j2000_hours = target_ra_j2000_hours
    slew_dec_j2000_degs = target_dec_j2000_degs + INITIAL_OFFSET_DEC_ARCMIN / 60.0

    print("Attempting to put RA %s, Dec %s (J2000) on pixel position (%.2f, %.2f)" % (
            convert.to_dms(target_ra_j2000_hours),
            convert.to_dms(target_dec_j2000_degs),
            TARGET_PIXEL_X_UNBINNED,
            TARGET_PIXEL_Y_UNBINNED
            ))

    for attempt_number in range(MAX_RESLEW_ATTEMPTS+1):
        # The mount expects Jnow coordinates, so we need to apply precession/nutation/etc.
        (slew_ra_jnow_hours, slew_dec_jnow_degs) = convert.j2000_to_jnow(slew_ra_j2000_hours, slew_dec_j2000_degs)
        
        #if attempt_number == 0:
        #    print "Performing offset slew"
        #    slew_dec_offset_degs = INITIAL_OFFSET_DEC_ARCMIN / 60.0
        #else:
        #    slew_dec_offset_degs = 0
            
        print("Attempt %d of %d" % (attempt_number+1, MAX_RESLEW_ATTEMPTS))
        print("Slewing to J2000 %s, %s" % (
            convert.to_dms(slew_ra_j2000_hours), 
            convert.to_dms(slew_dec_j2000_degs)
            ))
        
        mount.SlewToCoordinates(slew_ra_jnow_hours, slew_dec_jnow_degs)
        
        print("Settling...")
        time.sleep(SETTLE_TIME_SECONDS)
        
        print("Taking %d second exposure..." % (EXPOSURE_LENGTH_SECONDS_CENTER))
        camera.BinX = BINNING
        camera.BinY = BINNING
        camera.Expose(EXPOSURE_LENGTH_SECONDS_CENTER, 1)
        while not camera.ImageReady:
            time.sleep(0.1)
        
        print("Image complete")

        tempfilename = os.path.join(tempfile.gettempdir(), "center_pixel.fits")
        camera.SaveImage(tempfilename)

        if SAVE_IMAGES:
            filename = "image_%03d.fits" % (attempt_number)
            filepath = os.path.join(save_data_path, filename)
            print("Saving image to", filepath)
            camera.SaveImage(filepath)
            
        if attempt_number == 0:
            img = fits.open(filepath)
            head = img[0].header
            if head['pierside'] == 'EAST':
                MIRRORED = True
            else: 
                MIRRORED = False          
            
        print("Searching for WCS solution...")
        arcsec_per_pixel = ARCSEC_PER_PIXEL_UNBINNED * BINNING
        try:
            if VERBOSE_WCS_OUTPUT:
                print("----- WCS OUTPUT -------------------------------")

            talonwcs.talon_wcs(tempfilename, str(slew_ra_j2000_hours), str(slew_dec_j2000_degs), arcsec_per_pixel, MIRRORED, VERBOSE_WCS_OUTPUT)

            if VERBOSE_WCS_OUTPUT:
                print("----- END WCS OUTPUT ---------------------------")
        except Exception as ex:
            print("Unable to find WCS solution")
            print(ex.message)
            sys.exit(1)

        (target_radec_x_pixel, target_radec_y_pixel) = talonwcs.radec_to_xy(tempfilename, str(target_ra_j2000_hours), str(target_dec_j2000_degs))
        (ra_at_target_pixel_j2000_hours, dec_at_target_pixel_j2000_degs) = talonwcs.xy_to_radec(tempfilename, TARGET_PIXEL_X_UNBINNED/float(BINNING), TARGET_PIXEL_Y_UNBINNED/float(BINNING))

        error_x_pixels = TARGET_PIXEL_X_UNBINNED - target_radec_x_pixel*BINNING
        error_y_pixels = TARGET_PIXEL_Y_UNBINNED - target_radec_y_pixel*BINNING
        error_ra_hours = target_ra_j2000_hours - ra_at_target_pixel_j2000_hours
        error_dec_degs = target_dec_j2000_degs - dec_at_target_pixel_j2000_degs
        error_ra_arcsec = error_ra_hours*15*3600
        error_dec_arcsec = error_dec_degs*3600

        print("Current position error: %.2f pixels X, %.2f pixels Y" % (error_x_pixels, error_y_pixels))
        print("  RA error: %.2f arcsec,  Dec error: %.2f arcsec" % (error_ra_arcsec, error_dec_arcsec))

        if abs(error_x_pixels) < TOLERANCE_PIXELS and abs(error_y_pixels) < TOLERANCE_PIXELS:
            break

        slew_ra_j2000_hours += error_ra_hours
        slew_dec_j2000_degs += error_dec_degs
    else:
        print("Unable to position target within %.2f pixels after %d attempts. Aborting..." % (
                TOLERANCE_PIXELS,
                MAX_RESLEW_ATTEMPTS))
        return
        
    print("Target is now in position after %d attempts" % (attempt_number+1))

def parse_filepath_template(template):
    my_documents_path = os.path.expanduser(r'~\My Documents')
    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    
    template = template.replace('{MyDocuments}', my_documents_path)
    template = template.replace('{Timestamp}', timestamp)
    
    return template

if __name__ == "__main__":
    main()

