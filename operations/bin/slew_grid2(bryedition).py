from datetime import datetime
import math
import os
import time

from iotalib import VAOSpec
from iotalib import convert
from iotalib import rst

from win32com.client import Dispatch

### CONFIGURATION VALUES ########################

MOUNT_DRIVER = "ASCOM.SoftwareBisque.Telescope"  # Use this for the Paramount ME (controlled through TheSky)
#MOUNT_DRIVER = "SiTech.Telescope" # Use this for the SiTech-controlled Mathis fork mount at Winer Observatory

OBJECT_NAME = ""                    # Provides the name of an object to search for in the SIMBAD Database (If empty string, use provided coordinates)
CENTER_J2000_RA_HOURS = "07:53:30"  # RA coordinates at the center of the grid, in J2000 hours (HH:MM:SS.s)
CENTER_J2000_DEC_DEGS = "00:18:05"  # Dec coordinates at the center of the grid, in J2000 degrees (DD:MM:SS.s)
RASTER_GRID_RA_COLUMNS = 3          # Number of columns (distinct RA values) in the grid
RASTER_GRID_DEC_ROWS = 3            # Number of rows (distinct Dec values) in the grid
RA_GRID_SPACING_ARCSEC = 10         # RA spacing between each gridpoint, in arcseconds
DEC_GRID_SPACING_ARCSEC = 10        # Dec spacing between each gridpoint, in arcseconds
EQUAL_SKY_ANGLE = True              # If True, apply cos(dec) compensation to RA offsets so that the amount of apparent motion of the sky is the same regardless of declination

SETTLE_TIME_SECONDS = 3             # Pause for this many seconds after slewing to each target (and before taking an image, if requested)
PROMPT_BEFORE_STARTING_NEXT_TARGET = False # If True, script will wait for user to hit Enter before moving to each new target

TAKE_IMAGE_AT_EACH_GRIDPOINT = False # If True, Maxim DL will be used to take an image at each target
EXPOSURE_LENGTH_SECONDS = 3         # Exposure length of each image, in seconds
#PLATESOLVE_IMAGE = True             # If True, script will try to find the precise center RA/Dec of each image using PlateSolve2. NOT YET IMPLEMENTED
SAVE_IMAGES = False                 # If True, each image will be saved to SAVE_DATA_PATH
SAVE_DATA_PATH = r"{MyDocuments}\SlewGridData\{Timestamp}" # Script data (including coordinates.txt and FITS images) will be saved to this location.
RECORD_COORDINATES = True           # If True, write each J2000 coordinate to a file "coordinates.txt" in the data directory
TAKE_SPECTRA = True                 # If True, take spectra using Maya Spectrometer
SPEC_INT_TIME = 1                   # If TAKE_SPECTRA, specifies integration time of spectrometer

### END CONFIGURATION VALUES ########################


def main():
    """
    Starting point for the slew_grid script
    """
    global CENTER_J2000_RA_HOURS
    global CENTER_J2000_DEC_DEGS

    if(OBJECT_NAME!=""):
        finder = rst.ObjectFinder()
        inCoords = finder.sesame_resolve(OBJECT_NAME)
        CENTER_J2000_RA_HOURS = rst.hr2hms(inCoords[0])
        CENTER_J2000_DEC_DEGS = rst.deg2dms(inCoords[1])

    '''
    Getting the spectrometer ready
    '''

    print("Launching mount control software...")
    mount = Dispatch(MOUNT_DRIVER)

    print("Connecting to mount...")
    mount.Connected = True

    if TAKE_IMAGE_AT_EACH_GRIDPOINT:
        print("Launching MaxIm DL...")
        maxim = Dispatch("MaxIm.Application")
        maxim.LockApp = True

        camera = Dispatch("MaxIm.CCDCamera")
        camera.DisableAutoShutdown = True

        print("Connecting to camera...")
        camera.LinkEnabled = True

    if TAKE_SPECTRA:
        print("Connecting to spectrometer...")
        spec = VAOSpec.AvantesSpectrometer()
        print("Set spectrometer integration time to {0} secs".format(SPEC_INT_TIME))
        spec.setDevIntTime(SPEC_INT_TIME)
        print("Setting up spec table...")
        plotter = VAOSpec.mosaicPlotter(
            RASTER_GRID_DEC_ROWS, RASTER_GRID_RA_COLUMNS, spec.wavelengths)

    if mount.CanSetTracking:
        # Not all mount drivers support turning tracking on/off.
        # For example, the ASCOM driver for TheSky does not support it.
        # However, if it is supported, make sure tracking is on before slewing
        mount.Tracking = True

    targets = make_raster_scan_grid(
        convert.from_dms(CENTER_J2000_RA_HOURS),
        convert.from_dms(CENTER_J2000_DEC_DEGS),
        RASTER_GRID_RA_COLUMNS,
        RASTER_GRID_DEC_ROWS,
        RA_GRID_SPACING_ARCSEC,
        DEC_GRID_SPACING_ARCSEC,
        EQUAL_SKY_ANGLE)

    save_data_path = parse_filepath_template(SAVE_DATA_PATH)

    if (SAVE_IMAGES or RECORD_COORDINATES) and not os.path.isdir(save_data_path):
        print("Creating directory '%s'" % save_data_path)
        os.makedirs(save_data_path)

    target_number = 1
    for (target_ra_j2000_hours, target_dec_j2000_degs) in targets:
        # The mount expects Jnow coordinates, so we need to apply
        # precession/nutation/etc.
        (target_ra_jnow_hours, target_dec_jnow_degs) = convert.j2000_to_jnow(
            target_ra_j2000_hours, target_dec_j2000_degs)

        print()
        print("Target %d of %d" % (target_number, len(targets)))
        print("Slewing to J2000 %s, %s" % (
            convert.to_dms(target_ra_j2000_hours),
            convert.to_dms(target_dec_j2000_degs)
        ))

        mount.SlewToCoordinates(target_ra_jnow_hours, target_dec_jnow_degs)

        print("Settling...")
        time.sleep(SETTLE_TIME_SECONDS)

        if RECORD_COORDINATES:
            coords_filepath = os.path.join(save_data_path, "coordinates.txt")
            coords_file = open(coords_filepath, "a")
            print("%d, %f, %f" % (
                target_number, target_ra_j2000_hours, target_dec_j2000_degs), file=coords_file)
            coords_file.close()

        if TAKE_SPECTRA:
            print("Spec: Taking {0} second exposure...".format(SPEC_INT_TIME))
            spectra = spec.singleExposure()
            spec.saveLastSpec(save_data_path, target_number)
            plotter.addSpec(target_number, spectra)
            plotter.saveSpec(save_data_path)

        if TAKE_IMAGE_AT_EACH_GRIDPOINT:
            print("Camera: Taking %d second exposure..." % (EXPOSURE_LENGTH_SECONDS))
            camera.Expose(EXPOSURE_LENGTH_SECONDS, 1)
            while not camera.ImageReady:
                time.sleep(0.1)

            print("Image complete")

            if SAVE_IMAGES:
                filename = "image_%03d_ra_%f_dec_%f.fits" % (
                    target_number, target_ra_j2000_hours, target_dec_j2000_degs)
                filepath = os.path.join(save_data_path, filename)
                print("Saving image to", filepath)
                camera.SaveImage(filepath)

        if PROMPT_BEFORE_STARTING_NEXT_TARGET and target_number != len(targets):
            input("Press Enter to continue to next target...")

        target_number += 1

    print("Finished!")
    spec.close()


def make_raster_scan_grid(center_ra_hours, center_dec_degs, num_ra_columns, num_dec_rows, ra_spacing_arcsec, dec_spacing_arcsec, equal_sky_angle=True):
    """
    Create a grid of ra/dec coordinates following a "raster-scan" pattern; e.g.:

      1  2  3  4  5
      6  7  8  9  10
      11 12 13 14 15

    where point 8 = (center_ra_hours, center_dec_degs), num_ra_columns = 5, and num_dec_rows = 3

    If equal_sky_angle is true, cos(dec) compensation will be applied so that the target on
    the camera appears to move the same distance in both RA and Dec regardless of your
    current declination.

    Returns a list of RA-Dec tuples, with RA in hours and Dec in degrees. For example:

    [
     (1, 10),
     (2, 10),
     (3, 10),
     (1, 20),
     (2, 20),
     (3, 20),
     (1, 30),
     (2, 30),
     (3, 30)
    ]
    """

    targets = []

    for i in range(num_dec_rows):
        dec_steps_from_center = i - (num_dec_rows - 1) / 2.0
        dec_offset_degs = dec_steps_from_center * dec_spacing_arcsec / 3600.0
        target_dec_degs = center_dec_degs + dec_offset_degs

        for j in range(num_ra_columns):
            ra_steps_from_center = j - (num_ra_columns - 1) / 2.0
            ra_offset_degs = ra_steps_from_center * ra_spacing_arcsec / 3600.0
            if equal_sky_angle:
                ra_offset_degs = ra_offset_degs / \
                    math.cos(convert.degs_to_rads(target_dec_degs))

            target_ra_hours = center_ra_hours + \
                convert.degs_to_hours(ra_offset_degs)

            targets.append((target_ra_hours, target_dec_degs))

    return targets


def parse_filepath_template(template):
    my_documents_path = os.path.expanduser(r'~\My Documents')
    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")

    template = template.replace('{MyDocuments}', my_documents_path)
    template = template.replace('{Timestamp}', timestamp)

    return template

if __name__ == "__main__":
    main()
