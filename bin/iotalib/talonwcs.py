import math
import os
import subprocess
from subprocess import Popen, PIPE
import sys

from . import convert

# Calculate the path containing the WCS tools
THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
WCS_TOOLS_DIR = os.path.abspath(os.path.join(THIS_FILE_DIR, "..", "..", "wcs"))

# Calculate the path to each WCS executable
WCS_EXE = os.path.join(WCS_TOOLS_DIR, "wcs")
FITSHDR_EXE = os.path.join(WCS_TOOLS_DIR, "fitshdr")
RADEC2XY_EXE = os.path.join(WCS_TOOLS_DIR, "radec2xy")
XY2RADEC_EXE = os.path.join(WCS_TOOLS_DIR, "xy2radec")

def talon_wcs(filename, search_ra_hours, search_dec_degs, arcsec_per_pixel, mirrored=False, show_console_output=True):
    """
    Run the Talon "wcs" tool on a FITS image to search for a WCS solution.
    If successful, WCS headers will be added to the image.
    Some parameters can be edited in the "ip.cfg" file contained in the wcs directory.

    filename:         Path to the FITS file to process
    search_ra_hours:  Initial center RA to use when searching for a solution, in J2000 hours.
                      May be a float or a sexagesimal string
    search_dec_degs:  Initial center Dec to use when searching for a solution, in J2000 degrees.
                      May be a float or a sexagesimal string
    arcsec_per_pixel: Estimate of pixel size, in arcseconds
    mirrored:         Assuming that pixel (1, 1) is the top left pixel of the image,
                      this parameter should be False if the image can be rotated so that North is up
                      and East is left. The parameter should be True if the image can be rotated so
                      that North is up and East is right.

    Raises an exception if there is a problem running the tool or finding a solution
    """

    degs_per_pixel = arcsec_per_pixel/3600.0
    mirrored_sign = 1
    if mirrored:
        mirrored_sign = -1

    search_ra_hours = convert.from_dms(search_ra_hours)
    search_dec_degs = convert.from_dms(search_dec_degs)

    # Add the headers used by the WCS tool for the initial search parameters.
    subprocess.call([FITSHDR_EXE, "-r", "CDELT1", str(mirrored_sign*degs_per_pixel), filename])
    subprocess.call([FITSHDR_EXE, "-r", "CDELT2", str(degs_per_pixel), filename])
    subprocess.call([FITSHDR_EXE, "-r", "CRVAL1", str(search_ra_hours*15), filename])
    subprocess.call([FITSHDR_EXE, "-r", "CRVAL2", str(search_dec_degs), filename])
    subprocess.call([FITSHDR_EXE, "-s", "CTYPE1", "RA---TAN", filename])
    subprocess.call([FITSHDR_EXE, "-s", "CTYPE2", "DEC--TAN", filename])
    subprocess.call([FITSHDR_EXE, "-d", "RA", filename]) # Maxim's RA header (with spaces) can conflict with WCS tool
    subprocess.call([FITSHDR_EXE, "-d", "DEC", filename]) # Maxim's DEC header (with spaces) can conflict with WCS tool

    # Override the TELHOME environment variable so that we can use relative
    # paths when specifying the location of the GSC directory and ip.cfg
    environment = dict(TELHOME=WCS_TOOLS_DIR)

    stdout_destination = PIPE
    if show_console_output:
        stdout_destination = None

    process = Popen(
            [WCS_EXE,
             "-v", # Verbose
             "-w", # Allow FITS headers to be written
             "-o", # Overwrite any existing WCS headers
             "-i", "ip.cfg", # Specify the path to ip.cfg
             "-c", "gsc", # Specify the path to the GSC catalog
             filename],
            env=environment,
            stdout=stdout_destination,
            stderr=PIPE
            )

    (stdout, stderr) = process.communicate()  # Obtain stdout and stderr output from the wcs tool
    exit_code = process.wait() # Wait for process to complete and obtain the exit code

    if exit_code != 0:
        raise Exception("Error finding WCS solution.\n" +
                        "Exit code: " + str(exit_code) + "\n" + 
                        "Error output: " + stderr)


def xy_to_radec(filename, x, y):
    """
    Given a filename with Talon-compatible FITS headers, convert the specified
    (x, y) pixel position to a J2000 RA and Dec.

    Return a tuple containing (RA in hours, Dec in degrees)

    Raises an exception if there was a problem
    """

    process = Popen([XY2RADEC_EXE, filename, str(x), str(y)], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()
    exit_code = process.wait()

    if exit_code != 0:
        raise Exception("Error running xy2radec.\n" +
                        "Error code: " + str(exit_code) + "\n" +
                        "Stdout: " + stdout + "\n" +
                        "Stderr: " + stderr + "\n")

    try:
        (ra_rads, dec_rads) = [float(x) for x in stdout.split(" ")]
        ra_hours = math.degrees(ra_rads)/15.0
        dec_degs = math.degrees(dec_rads)

        return (ra_hours, dec_degs)
    except Exception as ex:
        raise Exception("Error parsing xy2radec output '%s'" % stdout)

def radec_to_xy(filename, ra_hours, dec_degs):
    """
    Given a filename with Talon-compatible FITS headers, convert the specified
    J2000 RA and Dec to an X,Y image pixel position.

    Return a tuple containing (x, y)

    Raises an exception if there was a problem
    """

    ra_hours = convert.from_dms(ra_hours)
    dec_degs = convert.from_dms(dec_degs)

    ra_rads = math.radians(ra_hours*15.0)
    dec_rads = math.radians(dec_degs)

    process = Popen([RADEC2XY_EXE, filename, str(ra_rads), str(dec_rads)], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()
    exit_code = process.wait()

    if exit_code != 0:
        raise Exception("Error running radec2xy.\n" +
                        "Error code: " + str(exit_code) + "\n" +
                        "Stdout: " + stdout + "\n" +
                        "Stderr: " + stderr + "\n")

    try:
        (x, y) = [float(x) for x in stdout.split(" ")]
        return (x, y)
    except Exception as ex:
        raise Exception("Error parsing radec2xy output '%s'" % stdout)

def clear_wcs_headers(filename):
    """
    Erase any existing WCS headers from an image
    """

    subprocess.call([WCS_EXE, "-w", "-d", filename])

    #wcs_keywords = [
    #    "CRPIX1",
    #    "CRPIX2",
    #    "CRVAL1",
    #    "CRVAL2",
    #    "CDELT1",
    #    "CDELT2",
    #    "CROTA1",
    #    "CROTA2",
    #    "CTYPE1",
    #    "CTYPE2"
    #    ]

    #for keyword in wcs_keywords:
    #    subprocess.call([FITSHDR_EXE, "-d", keyword, filename])

def main():
    #filename = "Ra1_Dec10_NorthDownEastRight.fit"
    #filename = "NorthUpEastLeft_longer.fit"
    #center_ra_hours = 1
    #center_dec_degs = 10
    #arcsec_per_pixel = 0.63
    #mirrored=False

    #filename = "../../wcs/crab.fits"
    #center_ra_hours = 5 + 34/60. + 40/3600.
    #center_dec_degs = 21 + 59/60. + 49/3600.
    #arcsec_per_pixel = 0.41
    #mirrored=True

    if len(sys.argv) < 5:
        print("Usage: talonwcs.py filename ra_hours dec_degs arcsec_per_pixel mirrored")
        sys.exit(1)

    filename = sys.argv[1]
    center_ra_hours = sys.argv[2]
    center_dec_degs = sys.argv[3]
    arcsec_per_pixel = float(sys.argv[4])
    if len(sys.argv) > 5:
        mirrored = (sys.argv[5].strip() == "1")
    else:
        mirrored = False

    clear_wcs_headers(filename)
    talon_wcs(filename, center_ra_hours, center_dec_degs, arcsec_per_pixel, mirrored)
    (ra, dec) = xy_to_radec(filename, 1000, 2000)
    print("ra, dec at (1000, 2000):", ra, dec)
    print("x, y:", radec_to_xy(filename, ra, dec))

if __name__ == "__main__":
    main()
