from datetime import datetime
import math
import os
import tempfile
import time
import sys

from iotalib import convert
from iotalib import talonwcs
from iotalib import rst

import ephem
from win32com.client import Dispatch

"""
This script should be called once the telescope has been manually positioned to place
a star at a desired location (e.g. on the spectrometer fiber or slit).

The script will take an image, find a WCS solution, and determine the pixel position
of the specified RA and Dec. Note that in the case of an off-axis fiber, the pixel
position may be outside the bounds of the CCD image.

The calibrated pixel position should be copied into the center_target_on_pixel script
so that the telescope can be automatically positioned to place new targets at the desired 
position.
"""

### CONFIGURATION VALUES ########################

OBJECT_NAME = ""                       # Provides the name of an object to search for in the SIMBAD Database (If empty string, use provided coordinates)
# TARGET_RA_J2000_HOURS = "18:36:56.543" # RA coordinates of the target star, in J2000 hours
# TARGET_DEC_J2000_DEGS = "38:47:05.713" # Dec coordinates of the target star, in J2000 degrees
TARGET_RA_J2000_HOURS = "18:36:53.9" # RA coordinates of the target star, in J2000 hours
TARGET_DEC_J2000_DEGS = "39:16:40.5" # Dec coordinates of the target star, in J2000 degrees

EXPOSURE_LENGTH_SECONDS = 5            # Exposure length of each image, in seconds

ARCSEC_PER_PIXEL_UNBINNED = 0.806       # Estimated image scale of UNBINNED image, in arcseconds per pixel
MIRRORED = False
VERBOSE_WCS_OUTPUT = True              # If True, output from the WCS script will be shown on the console in realtime. Useful for diagnosing WCS problems.

### END CONFIGURATION VALUES ########################


def main():
    """
    Starting point for the calibrate_target_pixel script
    """
    
    global TARGET_RA_J2000_HOURS, TARGET_DEC_J2000_DEGS
    
    if OBJECT_NAME != "":
        finder = rst.ObjectFinder()
        inCoords = finder.sesame_resolve(OBJECT_NAME)
        TARGET_RA_J2000_HOURS = rst.hr2hms(inCoords[0])
        TARGET_DEC_J2000_DEGS = rst.deg2dms(inCoords[1])

    print("Launching MaxIm DL...")
    maxim = Dispatch("MaxIm.Application")
    maxim.LockApp = True
    
    camera = Dispatch("MaxIm.CCDCamera")
    camera.DisableAutoShutdown = True

    print("Connecting to camera...")
    camera.LinkEnabled = True
    
    target_ra_j2000_hours = str(convert.from_dms(TARGET_RA_J2000_HOURS))
    target_dec_j2000_degs = str(convert.from_dms(TARGET_DEC_J2000_DEGS))

    print("Taking %d second exposure..." % (EXPOSURE_LENGTH_SECONDS))
    camera.BinX = 1
    camera.BinY = 1
    camera.Expose(EXPOSURE_LENGTH_SECONDS, 1)
    while not camera.ImageReady:
        time.sleep(0.1)
    
    print("Image complete")

    tempfilename = os.path.join(tempfile.gettempdir(), "center_pixel.fits")
    camera.SaveImage(tempfilename)

    print("Searching for WCS solution...")
    try:
        if VERBOSE_WCS_OUTPUT:
            print("----- WCS OUTPUT -------------------------------")
        print(tempfilename, target_ra_j2000_hours, target_dec_j2000_degs, ARCSEC_PER_PIXEL_UNBINNED, MIRRORED, VERBOSE_WCS_OUTPUT)
        talonwcs.talon_wcs(tempfilename, target_ra_j2000_hours, target_dec_j2000_degs, ARCSEC_PER_PIXEL_UNBINNED, MIRRORED, VERBOSE_WCS_OUTPUT)

        if VERBOSE_WCS_OUTPUT:
            print("----- END WCS OUTPUT ---------------------------")
    except Exception as ex:
        print("Unable to find WCS solution")
        print(ex.message)
        sys.exit(1)

    (target_radec_x_pixel, target_radec_y_pixel) = talonwcs.radec_to_xy(tempfilename, target_ra_j2000_hours, target_dec_j2000_degs)
    print("Target J2000 RA %s, Dec %s is located at pixel position:" % (TARGET_RA_J2000_HOURS, TARGET_DEC_J2000_DEGS))
    print("TARGET_PIXEL_X_UNBINNED = %.3f" % (target_radec_x_pixel))
    print("TARGET_PIXEL_Y_UNBINNED = %.3f" % (target_radec_y_pixel))

if __name__ == "__main__":
    main()

