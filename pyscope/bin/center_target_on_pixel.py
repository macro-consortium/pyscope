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

import relimport # Update PYTHONPATH to find iotalib

import logging
import os

from iotalib import center_target
from iotalib import config_observatory
from iotalib import config_wcs
from iotalib import convert
from iotalib import observatory
from iotalib import talonwcs
from iotalib import rst




### CONFIGURATION VALUES ########################

# NOTE: See wcs.cfg to set pixel scale and mirroring settings

OBJECT_NAME = ""                       # Provides the name of an object to search for in the SIMBAD Database (If empty string, use provided coordinates)
TARGET_RA_J2000_HOURS = "18:36:56.57" # RA coordinates of the target star, in J2000 hours
TARGET_DEC_J2000_DEGS = "+38:47:06.299" # Dec coordinates of the target star, in J2000 degrees
TARGET_PIXEL_X_UNBINNED = 1021.2      # Target X pixel position in unbinned image. Center of the top left corner pixel is (1, 1)
TARGET_PIXEL_Y_UNBINNED = 3069.5     # Target Y pixel position in unbinned image. Center of the top left corner pixel is (1, 1)
TOLERANCE_PIXELS = 1                   # Continue refining pointing until target RA/Dec is within this many pixels of target pixel location
CHECK_AND_REFINE = True                # If True, continue imaging and recentering until within tolerance (up to MAX_RESLEW_ATTEMPTS). If False, image and recenter once without re-checking
MAX_RESLEW_ATTEMPTS = 5                # Give up after trying to refine pointing this many times
INITIAL_OFFSET_DEC_ARCMIN = 27.65          # Offset for first image, to avoid blooming on bright target

EXPOSURE_LENGTH_SECONDS = 10            # Exposure length of each image, in seconds
BINNING = 1                            # Image binning (higher binning reduces resolution but speeds up image readout time) 

SAVE_IMAGES = False                    # If True, each image will be saved to SAVE_DATA_PATH
SAVE_DATA_PATH = r"{MyDocuments}\CenterTargetData\{Timestamp}" # Script data will be saved to this location.

VERBOSE_WCS_OUTPUT = True              # If True, output from the WCS script will be shown on the console in realtime. Useful for diagnosing WCS problems.
SYNC_MOUNT = False                      # If True, the entire coordinate system of the mount will be offset (i.e. offsets apply to future slews)

### END CONFIGURATION VALUES ########################


def main():
    """
    Starting point for the center_target_on_pixel script
    """

    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    config_observatory.read()
    config_wcs.read()
    observatory.setup_mount()
    observatory.setup_camera()
    
    if OBJECT_NAME == "":
        target_ra_j2000_hours = convert.from_dms(TARGET_RA_J2000_HOURS)
        target_dec_j2000_degs = convert.from_dms(TARGET_DEC_J2000_DEGS)
    else:
        finder = rst.ObjectFinder()
        inCoords = finder.sesame_resolve(OBJECT_NAME)
        target_ra_j2000_hours = rst.hr2hms(inCoords[0])
        target_dec_j2000_degs = rst.deg2dms(inCoords[1])


    center_target.target_ra_j2000_hours = target_ra_j2000_hours
    center_target.target_dec_j2000_degs = target_dec_j2000_degs
    center_target.target_pixel_x_unbinned = TARGET_PIXEL_X_UNBINNED
    center_target.target_pixel_y_unbinned = TARGET_PIXEL_Y_UNBINNED
    center_target.initial_offset_dec_arcmin = INITIAL_OFFSET_DEC_ARCMIN
    center_target.check_and_refine = CHECK_AND_REFINE
    center_target.max_reslew_attempts = MAX_RESLEW_ATTEMPTS
    center_target.tolerance_pixels = TOLERANCE_PIXELS
    center_target.exposure_length_seconds = EXPOSURE_LENGTH_SECONDS
    center_target.binning = BINNING
    center_target.save_images = SAVE_IMAGES
    center_target.save_data_path_template = SAVE_DATA_PATH
    center_target.write_wcs_stdout_to_console = VERBOSE_WCS_OUTPUT
    center_target.sync_mount = SYNC_MOUNT

    result = center_target.center_coordinates_on_pixel()
    logging.info("FINAL RESULT: %s", result)


if __name__ == "__main__":
    main()

