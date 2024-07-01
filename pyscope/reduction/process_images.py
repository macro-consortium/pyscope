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


def sort_image(img, dest):
    """copy image to a directory, create it if needed"""
    if not dest.exists():
        dest.mkdir(mode=0o775, parents=True)
    target = dest / img.name
    shutil.copy(img, target)


def store_image(img, dest, update_db=False):
    """store copy of image in long-term archive directory :dest
    check that the target is older or doesn't exist
    log errors
    future: use s3cmd library to interact with object storage more efficiently
    future: update_db=True adds image info to database
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
    """process a single image
    calibrate if needed
    move to reduced or failed depending on status
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
