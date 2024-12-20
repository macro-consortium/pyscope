#!/usr/bin/env python
"""A systemd process to dynamically calibrate and distribute incoming FITS images

This is the contents of the systemd service file used to run this on chronos:

[Unit]
Description=PyScope Incoming Image Processing
After=local-fs.target

[Service]
Type=simple
ExecStart=/usr/local/telescope/bin/process-images
User=rlmt
Group=rlmt
Restart=on-failure
Environment="PATH=/opt/miniforge3/bin:/usr/local/telescope/bin:/usr/local/bin:/usr/bin"

[Install]
WantedBy=multi-user.target

"""

import datetime as dt
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from astropy.io import fits

from pyscope.reduction.calib_images import calib_images

# observatory home - TODO get from environment?
OBSERVATORY_HOME = Path("/usr/local/telescope/rlmt")

# directory where raw images arrive
LANDING_DIR = Path(OBSERVATORY_HOME, "images")

# calibration images
CALIB_DIR = Path(LANDING_DIR, "calibrations", "masters")

# long term storage
STORAGE_ROOT = Path("/mnt/imagesbucket")

# maximum age in seconds
MAXAGE = 7 * 3600 * 24

# maximum time since modification in seconds
MAXMTIME = 1 * 3600 * 24

# configure the logger - >INFO to log, >DEBUG to console
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(OBSERVATORY_HOME / "logs/process-images.log")
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fmt = logging.Formatter("Process-images: %(asctime)s:%(levelname)s:%(message)s")
fh.setFormatter(fmt)
ch.setFormatter(fmt)
logger.addHandler(fh)
logger.addHandler(ch)


def runcmd(cmd, **kwargs):
    """Run a subprocess"""
    return subprocess.run(
        cmd, shell=True, capture_output=True, encoding="ascii", **kwargs
    )


def isCalibrated(img):
    """
    Checks if a FITS image has calibration started.

    Parameters
    ----------
    img : `pathlib.Path`
        Path to the FITS image file.

    Returns
    -------
    bool
        `True` if the FITS header contains the `CALSTART` keyword, `False` otherwise.
    """
    try:
        fits.getval(img, "CALSTART")
    except KeyError:
        return False
    else:
        return True


def isSuccessfullyCalibrated(img):
    """Returns `True` if calibration was completed successfully,
    `False` otherwise
    """
    try:
        fits.getval(img, "CALSTAT")
    except KeyError:
        return False
    else:
        return True


def sort_image(img, dest):
    """Copy image to a directory, create it if needed"""
    if not dest.exists():
        dest.mkdir(mode=0o775, parents=True)
    target = dest / img.name
    shutil.copy(img, target)


def store_image(img, dest, update_db=False):
    """
    Archives a FITS image in a long-term storage directory.

    Copies the file to the specified directory if the target does not exist or 
    is older than the source. Logs errors during the copy process.

    Parameters
    ----------
    img : `pathlib.Path`
        Path to the FITS image file.
    dest : `pathlib.Path`
        Destination directory for storing the image.
    update_db : `bool`, optional
        If `True`, updates the database with image metadata. (Future implementation)

    Returns
    -------
    bool
        `True` if the file is successfully copied, `False` otherwise.
    """
    if not dest.exists():
        dest.mkdir(mode=0o775, parents=True)
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
    """
    Processes a single FITS image by calibrating and classifying it based on the outcome. 

    The function begins by reading the FITS file data and header. If the image has not 
    already been calibrated, it applies calibration using the `calib_images` function. 
    Once calibrated, the image is moved to a `reduced` directory if the calibration is 
    successful or a `failed` directory if calibration fails. Regardless of the outcome, 
    the image is archived in a long-term storage directory for later use. Finally, the 
    image is removed from the landing directory to complete the process.

    Parameters
    ----------
    img : `pathlib.Path`
        Path to the FITS image file to process.

    Raises
    ------
    Exception
        If the image is corrupt or calibration fails.
    """
    logger.info(f"Processing {img}...")
    try:
        data, hdr = fits.getdata(img), fits.getheader(img, 0)
    except:
        sort_image(img, img.parent / "failed")
        logger.exception(f"Corrupt FITS file {img}")
        img.unlink()
        return

    img_isodate = fits.getval(img, "DATE-OBS")[:10]

    if not isCalibrated(img):
        fil = fits.getval(img, "FILTER").strip().lower()

        # store a copy of the raw image in long-term storage
        store_image(img, STORAGE_ROOT / "rawimage" / img_isodate)

        # send this single image to calib_images
        try:
            calib_images(
                camera_type="ccd",
                image_dir=None,
                calib_dir=CALIB_DIR,
                raw_archive_dir=LANDING_DIR / "raw_archive",
                in_place=True,
                zmag=True,
                verbose=0,
                fnames=(img,),
            )
        except:
            sort_image(img, img.parent / "failed")
            logger.exception(
                f"calib_images failed on image {img}: no matching calibration frames maybe?"
            )
            img.unlink()
            return

        # calculate fwhm assuming we're still doing this..
        if fil not in ("lrg", "hrg"):
            runcmd(f"fwhm -ow {img}")

    if isSuccessfullyCalibrated(img):
        sort_image(img, img.parent / "reduced")
        store_image(img, STORAGE_ROOT / "reduced" / img_isodate)

    else:
        sort_image(img, img.parent / "failed")
        logger.warning(f"Calibration failed on {img}")

    img.unlink()


if __name__ == "__main__":

    os.umask(0o002)

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
            # if the image has not been modified in MAXTIME seconds and has a date older than MAXAGE, remove it
            if img.exists() and time.time() - img.stat().st_mtime > MAXMTIME:
                try:
                    img_isodate = fits.getval(img, "DATE-OBS")[:10]
                except:
                    continue
                yyyy, mm, dd = [int(s) for s in img_isodate.split("-")]
                age = (
                    time.time()
                    - dt.datetime(yyyy, mm, dd, tzinfo=dt.timezone.utc).timestamp()
                )
                if age > MAXAGE:
                    img.unlink()
                    logger.info(f"Deleted {img}")
