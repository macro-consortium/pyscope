#!/usr/bin/env python
"""A systemd process to dynamically calibrate and distribute incoming FITS images

This is the contents of the systemd service file used to run this on chronos:

[Unit]
Description=PyScope Incoming Image Processing
After=local-fs.target

[Service]
Type=simple
ExecStart=/usr/local/telescope/bin/process-images
User=talon
Group=talon
Restart=on-failure
Environment="PATH=/opt/miniforge3/bin:/usr/local/telescope/bin:/usr/local/bin:/usr/bin"

[Install]
WantedBy=multi-user.target

"""

import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime as dt
from pathlib import Path

from astropy.io import fits

from .calib_images import calib_images

# observatory home - get this from the environment instead?
OBSERVATORY_HOME = Path("/usr/local/telescope/rlmt")

# directory where raw images arrive
# LANDING_DIR = Path(OBSERVATORY_HOME, 'images')
LANDING_DIR = Path("/mnt/ExtraImages")

# calibration files directory
CALIB_DIR = Path(OBSERVATORY_HOME, "images", "calibrations", "masters")

# long term storage
STORAGE_ROOT = Path("/mnt/imagesbucket")

# maximum age in seconds
MAXAGE = 7 * 3600 * 24

# image prefixes and group names
groups = dict(m="macalester", a="augustana", c="coe", k="knox", i="iowa", x="external")

# RA's in Sloan catalog at 30 deg Dec
sloan_ra = [22, 23, 0, 1, 2, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

# configure the logger - >INFO to log, >DEBUG to console
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(OBSERVATORY_HOME / "logs/process-images.log")
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fmt = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
fh.setFormatter(fmt)
ch.setFormatter(fmt)
logger.addHandler(fh)
logger.addHandler(ch)


def runcmd(cmd, **kwargs):
    """run a subprocess"""
    return subprocess.run(
        cmd, shell=True, capture_output=True, encoding="ascii", **kwargs
    )


def isCalibrated(img):
    """returns True if calibration was started,
    False otherwise
    """
    try:
        fits.getval(img, "CALSTART")
    except KeyError:
        return False
    else:
        return True


def isSuccessfullyCalibrated(img):
    """returns True if calibration was completed successfully,
    False otherwise
    """
    try:
        fits.getval(img, "CALSTAT")
    except KeyError:
        return False
    else:
        return True


def store_image(img, dest, update_db=False):
    """store image in long-term archive directory :dest
    check that the target is older or doesn't exist
    log errors
    future: use s3cmd library to interact with object storage more efficiently
    future: update_db=True adds image info to database
    """
    if not dest.exists():
        dest.mkdir(mode=0o775)
    target = dest / img.name
    if not target.exists() or target.stat().st_mtime < img.stat().st_mtime:
        try:
            shutil.copy(img, target)
        except:
            logger.exception(f"Unable to store {target}")
            return False
        else:
            logger.info(f"Copied {img.name} -> {target}")
            return True


def process_image(img):
    """process a single image
    calibrate if needed
    move to reduced or failed depending on status
    """
    try:
        header = fits.getheader(img, 0)
    except OSError:
        logger.exception(f"Corrupt FITS file {img}")
        return

    img_isodate = fits.getval(img, "DATE-OBS")[:10]

    if not isCalibrated(img):
        fil = fits.getval(img, "FILTER").strip().lower()

        # store a copy of the raw image in long-term storage
        store_image(img, STORAGE_ROOT / "rawimage" / img_isodate)

        # Calculate zero-point magnitudes for foc images that are have Sloan filters and are in Sloan catalog
        # NB overwrite switch on to override ZAG solution from Pinpoint
        zmag = False
        if img.name[:3] == "foc":
            ra = round(float(fits.getval(img, "RA")[:2]))
            if fil in ("g", "r", "i") and ra in sloan_ra:
                zmag = True

        # send this single image to calib_images
        calib_images(
            camera_type=CAMERA_TYPE,
            calib_dir=CALIB_DIR,
            image_dir=None,
            fnames=[img],
            raw_archive_dir=img.parent / "raw_archive",
            in_place=True,
            wcs=False,
            zmag=zmag,
            verbose=False,
        )

        # calculate fwhm assuming we're still doing this..
        if fil not in ("lrg", "hrg"):
            runcmd(f"fwhm -ow {img}")

    if isSuccessfullyCalibrated(img):
        temp = img.parent / "reduced"
        if not temp.exists():
            temp.mkdir(mode=0o775)
        shutil.copy(img, temp)
        groupdir = groups.get(img.name[0], "other")
        store_image(img, STORAGE_ROOT / groupdir / img_isodate)

    elif isCalibrated(img):
        failed = img.parent / "failed"
        if not failed.exists():
            failed.mkdir(mode=0o775)
        shutil.copy(img, failed)
        logger.warning(f"Calibration failed on {img}")

    img.unlink()


if __name__ == "__main__":

    os.umask(0o002)

    # Can specify file(s) on command line
    # in which case script exits when specified files are processed
    # but probably shouldn't -- better to run calib_images directly
    if len(sys.argv) > 1:
        if runcmd("id -gn").stdout.strip() != "talon":
            sys.exit("Must be run as 'talon' user or group")
        file_list = [Path(x) for x in sys.argv[1:]]
        for img in file_list:
            process_image(img)

    # with no arguments, run continuously
    else:
        while True:
            fresh = []
            done = []
            for ext in (".fts", ".fits", ".fit"):
                fresh.extend(LANDING_DIR.glob(f"*{ext}"))
                for d in ("raw_archive", "reduced", "failed"):
                    done.extend((LANDING_DIR / d).rglob(f"*{ext}"))

            time.sleep(5)

            for img in fresh:
                process_image(img)

            for img in done:
                if img.exists() and time.time() - img.stat().st_mtime > MAXAGE:
                    img.unlink()
                    logger.info(f"Deleted {img}")
