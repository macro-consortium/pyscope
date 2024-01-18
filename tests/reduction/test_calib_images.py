import pytest
from astropy.io import fits
from pyscope.reduction import calib_images
import numpy as np
import os
import shutil
import pathlib
import glob
import requests


def test_latest_calib_set_when_no_calib_dir():
    """
    Test that calib_images works when there is no calib_dir passed.
    """
    path = os.getcwd()
    
    if os.getenv("observatory_home") is None:
        os.environ["observatory_home"] = path + "/observatory_home"
    
    home_loc = os.getenv("observatory_home")  # environment variable must be defined
    
    get_raw_images()
    generate_calib_files()
    
    # check that the necessary files locations exist
    masters_loc = pathlib.Path(home_loc + "/images/masters")
    raw_loc = pathlib.Path(home_loc + "/images/raw")
    raw_archive_loc = pathlib.Path(home_loc + "/images")
    
    assert os.path.exists(masters_loc)
    assert os.path.exists(raw_loc)
    assert os.path.exists(raw_archive_loc)
    

    uncalibrated = []
    for file in os.listdir(raw_loc):
        uncalibrated.append(file)

    calib_images(image_dir=raw_loc)  # running calib_images with no calib_dir
    
    for file in uncalibrated:
        assert os.path.exists(f"{raw_loc}/{file[:-4]}_cal.fts")

    delete_calib_files()
    
    return
    

def test_latest_calib_set_when_calib_dir():
    
    pass


def get_raw_images():
    """
    TODO: Finish
    Get series of raw images from the MACRO website and store them in the temporary folder, raw, in images.
    """
    home_loc = os.getenv("observatory_home")
    os.makedirs(f"{home_loc}/images/raw", exist_ok=True)
    url = "https://macroconsortium.org/images/macalester/maw/2023/332/maw332a0.fts"
    r = requests.get(url, allow_redirects=True)
    open(pathlib.Path(f'{home_loc}/images/raw/maw332a0.fts'), 'wb').write(r.content)
    
    return


def generate_calib_files():
    """
    Generate a series of 1x1 test fits files to use as calib images.
    """
    # TODO: verify these are the correct options for a calibration file
    calib_types = ["master_flat", "master_dark", "master_bias", "master_flat_dark"]
    filters = ["L", 6, "V", "B", "H", "W", "O", 1, "I", "X", "G", "R"]
    readouts = ["HighGain", "LowGain", "HighGainStackPro", "HDR"]
    exposure_times = [float(2**i) for i in range(-3,11)]
    xbins = [1, 2]
    ybins = [1, 2]

    home_loc = os.getenv("observatory_home")
    loc = f"{home_loc}/images/masters"
    os.makedirs(loc, exist_ok=True)

    for calib_type in calib_types:
        for filt in filters:
            for readout in readouts:
                for exptime in exposure_times:
                    for xbin in xbins:
                        for ybin in ybins:
                            data = np.zeros((1, 1), dtype=np.float64)
                            hdu = fits.PrimaryHDU(data=data)

                            hdu.header["FILTER"] = filt
                            hdu.header["READOUTM"] = readout
                            hdu.header["EXPTIME"] = exptime
                            hdu.header["XBINNING"] = xbin
                            hdu.header["YBINNING"] = ybin

                            if calib_type == "master_flat":
                                hdu.writeto(f'{loc}/{calib_type}_{filt}_{readout}_{exptime}_{xbin}x{ybin}.fts', overwrite=True)

                            elif calib_type == "master_dark":
                                hdu.writeto(f'{loc}/{calib_type}_{readout}_{exptime}_{xbin}x{ybin}.fts', overwrite=True)

                            elif calib_type == "master_bias":
                                hdu.writeto(f'{loc}/{calib_type}_{readout}_{xbin}x{ybin}.fts', overwrite=True)

                            elif calib_type == "master_flat_dark":
                                hdu.writeto(f'{loc}/{calib_type}_{readout}_{exptime}_{xbin}x{ybin}.fts', overwrite=True)
    return


def delete_calib_files():
    """
    Detete the test fits files used as calib images. Note that this will delete the masters
    directory, but keep the images parent directory.
    """
    shutil.rmtree("observatory_home/images/masters/")
    for file in glob.glob("observatory_home/images/raw/*"):
        if file.endswith("_cal.fts"):
            os.remove(file)
    return


def test_have_env_var():
    """
    Test that the environment variable, observatory_home, is defined.
    """
    home_loc = os.getenv("observatory_home")
    assert home_loc is not None
    return

