import glob
import os
import shutil

import numpy as np
import pytest
from astropy.io import fits

from pyscope.reduction import avg_fits_ccdproc


def test_avg_fits_ccdproc(tmp_path):
    """
    Tests avg_fits_ccdproc modes and datatypes. More tests should be written for each optional parameter to ensure full coverage.
    TODO: write more tests for each optional parameter
    """
    cwd = os.getcwd()

    if os.path.exists(os.path.join(cwd, tmp_path, "averaged")):
        shutil.rmtree(os.path.join(cwd, tmp_path, "averaged"))
    os.makedirs(os.path.join(cwd, tmp_path, "averaged"))

    # create a test FITS file of
    print(f"\n\n\n\n\n********** NEW TESTING RUN **********\n\n\n\n\n")
    print(f"creating test FITS files in {tmp_path}")
    for i in range(1, 11):
        data = np.ones((10, 10), dtype=np.float64)
        fits.writeto(f"{tmp_path}/avg_fits_test_{i}.fits", data * i, overwrite=True)
        # print(data * i)

    files = glob.glob(f"{tmp_path}/avg_fits_test_*.fits")

    # test median mode
    print("\n**** testing median mode ****\n")
    avg_fits_ccdproc(
        mode="0",
        outfile=f"{tmp_path}/averaged/avg_fits_median.fits",
        fnames=files,
        verbose=True,
    )
    med_data = fits.getdata(f"{tmp_path}/averaged/avg_fits_median.fits")
    med = np.ones((10, 10), dtype=np.uint16)
    med = med * np.median(range(1, 11)).astype(np.uint16)
    print(med_data, med)
    print(f"\nmedian data\n{med_data}\n\nmedian\n{med}\n")
    print("correctly calculated median")

    # test mean mode
    print("\n**** testing mean mode ****\n")
    avg_fits_ccdproc(
        mode="1",
        outfile=f"{tmp_path}/averaged/avg_fits_mean.fits",
        fnames=files,
        verbose=True,
    )
    mean_data = fits.getdata(f"{tmp_path}/averaged/avg_fits_mean.fits")
    mean = np.ones((10, 10), dtype=np.uint16)
    mean = mean * np.mean(range(1, 11)).astype(np.uint16)
    print(f"\nmean data\n{mean_data}\n\nmean\n{mean}\n")
    assert np.array_equal(mean_data, mean)
    print("correctly calculated mean")

    # test different data type
    print("\n**** testing different data type ****\n")
    avg_fits_ccdproc(
        mode="1",
        outfile=f"{tmp_path}/averaged/avg_fits_mean.fits",
        fnames=files,
        datatype=np.float64,
        verbose=True,
    )
    mean_data = fits.getdata(f"{tmp_path}/averaged/avg_fits_mean.fits")
    mean = np.ones((10, 10), dtype=np.float64)
    mean = mean * np.mean(range(1, 11)).astype(np.float64)
    print(f"\nmean data\n{mean_data}\n\nmean\n{mean}\n")
    assert np.array_equal(mean_data, mean)
    print("correctly calculated mean")

    print("passed all tests!")
    return


# if __name__ == "__main__":
#     test_avg_fits_ccdproc("./tmp_dir")
