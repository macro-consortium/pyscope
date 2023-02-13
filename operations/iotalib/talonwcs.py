# Built-in Python imports
import logging
import math
import os
import subprocess
from subprocess import Popen, PIPE
import sys

# iotalib imports
from . import convert
from . import paths

# Calculate the path to each WCS executable
WCS_EXE = paths.talon_wcs_path("wcs")
FITSHDR_EXE = paths.talon_wcs_path("fitshdr")
RADEC2XY_EXE = paths.talon_wcs_path("radec2xy")
XY2RADEC_EXE = paths.talon_wcs_path("xy2radec")

def talon_wcs(filename, search_ra_hours, search_dec_degs, arcsec_per_pixel, mirrored=False, write_stdout_to_console=True, search_radius_degs=1):
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
    write_stdout_to_console: If True, output will go directly to the console rather than being
                         routed through the normally logging routines. Useful for seeing
                         output from a long-running WCS process in realtime.
    search_radius_degs: Spiral out from center coordinates searching for a match; give up after
                        moving this far from center without success.

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

    return run_wcs(
        "-v", # Verbose
        "-w", # Allow FITS headers to be written
        "-o", # Overwrite any existing WCS headers
        "-u", search_radius_degs,  # Specify search radius, in degrees
        filename,
        write_stdout_to_console=write_stdout_to_console
    )
    
def run_wcs(*args, **kwargs):
    """
    Set up the environment and run the bundled wcs.exe (from the Talon distribution)
    using the supplied command line arguments
    """
    
    # Pull out keyword args that we are interested in
    write_stdout_to_console = kwargs.get("write_stdout_to_console", False)
    
    # Override the TELHOME environment variable so that we can use relative
    # paths when specifying the location of the GSC directory and ip.cfg
    environment = dict(TELHOME=paths.talon_wcs_path())

    stdout_destination = PIPE
    if write_stdout_to_console:
        stdout_destination = None

    # Make sure all passed-in arguments are strings
    args = [str(x) for x in args]

    args = [
        WCS_EXE,
        # wcs.exe will use the last-specified values for -i and -c, so
        # we'll provide defaults below but they can be overridden by values
        # coming in via the *args array
        "-i", "ip.cfg", # Specify the path to ip.cfg (relative to TELHOME)
        "-c", "gsc" # Specify the path to the GSC catalog (relative to TELHOME)
    ] + list(args) # Include additional args specified by the user
    
    process = Popen(
            args,
            env=environment,
            stdout=stdout_destination,
            stderr=PIPE
            )

    (stdout, stderr) = process.communicate()  # Obtain stdout and stderr output from the wcs tool
    exit_code = process.wait() # Wait for process to complete and obtain the exit code

    if not write_stdout_to_console:
        logging.info(stdout.decode("utf-8"))

    if exit_code != 0:
        logging.info("Error finding WCS solution.\n" +
                        "Exit code: " + str(exit_code) + "\n" + 
                        "Error output: " + stderr.decode("utf-8"))
        return False
    return True


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
        (ra_rads, dec_rads) = [float(x) for x in stdout.decode("utf-8").split(" ")]
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
        (x, y) = [float(x) for x in stdout.decode("utf-8").split(" ")]
        return (x, y)
    except Exception as ex:
        raise Exception("Error parsing radec2xy output '%s'" % stdout.decode("utf-8"))

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
    #filename = "D:\IOTA3\images\transferred"
    #filename = "NorthUpEastLeft_longer.fit"
    #center_ra_hours = 22.087
    #center_dec_degs = 53.5102
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
