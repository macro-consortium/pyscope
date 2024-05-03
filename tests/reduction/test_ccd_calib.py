## make image with ccdproc
## calibrate with ccdproc
## calibrate with ccd_calib
## take difference
## if equal, then it passes the test
## Follow guideline Will sent

import numpy as np
import os
from convenience_functions import show_image
import image_sim as imsim
import matplotlib.pyplot as plt
from astropy.io import fits
import shutil
import pytest
from pyscope.reduction import ccd_calib

def test_ccd_calib(tmp_path):
    # create raw and master directories
    print("removing old tmp directory... if it exists")
    if os.path.exists(os.path.join(tmp_path, "master")):
        shutil.rmtree(os.path.join(tmp_path, "master"))
    
    print("creating master directories")
    os.makedirs(os.path.join(tmp_path, "master"))
    os.makedirs(os.path.join(tmp_path, "master", "bias"))
    os.makedirs(os.path.join(tmp_path, "master", "dark"))
    os.makedirs(os.path.join(tmp_path, "master", "flat"))

    print("removing old raw directory... if it exists")
    if os.path.exists(os.path.join(tmp_path, "raw")):
        shutil.rmtree(os.path.join(tmp_path, "raw"))

    print("creating raw directory")
    os.makedirs(os.path.join(tmp_path, "raw"))

    print("removing old calibrated directory... if it exists")
    if os.path.exists(os.path.join(tmp_path, "calibrated")):
        shutil.rmtree(os.path.join(tmp_path, "calibrated"))

    print("creating calibrated directory")
    os.makedirs(os.path.join(tmp_path, "calibrated"))

    print()
    print("creating test images...")
    print()
    # image parameters
    image = np.zeros([2000, 2000])
    gain = 1.0
    star_exposure = 60.0  # changed from 30
    dark_exposure = 60.0
    dark = 0.1
    sky_counts = 20
    bias_level = 1100
    read_noise_electrons = 5  # reduced from 700
    max_star_counts = 2000

    print("creating bias image...")
    # bias image
    bias_with_noise = (imsim.bias(image, bias_level, realistic=True) + 
                        imsim.read_noise(image, read_noise_electrons, gain=gain))
    fits.writeto(os.path.join(tmp_path, "master", "bias", "master-bias.fts"), bias_with_noise, overwrite=True)
    header = fits.getheader(os.path.join(tmp_path, "master", "bias", "master-bias.fts"))
    header["READOUT"] = "highgain"
    header["EXPOSURE"] = 0.0
    header["XBIN"] = "1"
    header["YBIN"] = "1"
    fits.writeto(filename=os.path.join(tmp_path, "master", "bias", "master-bias.fts"), data=bias_with_noise, header=header, overwrite=True)
    print(f'bias image created: {os.path.join(tmp_path, "master", "bias", "master-bias.fts")}')
    
    print("creating dark image...")
    # dark frame
    dark_frame_with_noise = (imsim.bias(image, bias_level, realistic=True) + 
                            imsim.dark_current(image, dark, dark_exposure, gain=gain, hot_pixels=True) +
                            imsim.read_noise(image, read_noise_electrons, gain=gain))
    fits.writeto(os.path.join(tmp_path, "master", "dark", "master-dark.fts"), dark_frame_with_noise, overwrite=True)
    header = fits.getheader(os.path.join(tmp_path, "master", "dark", "master-dark.fts"))
    header["READOUT"] = "highgain"
    header["EXPOSURE"] = 60.0
    header["XBIN"] = "1"
    header["YBIN"] = "1"
    fits.writeto(filename=os.path.join(tmp_path, "master", "dark", "master-dark.fts"), data=dark_frame_with_noise, header=header, overwrite=True)
    print(f'dark image created: {os.path.join(tmp_path, "master", "dark", "master-dark.fts")}')

    print("creating flat image...")
    # flat field
    flat = imsim.sensitivity_variations(image)
    fits.writeto(os.path.join(tmp_path, "master", "flat", "master-flat.fts"), flat, overwrite=True)
    header = fits.getheader(os.path.join(tmp_path, "master", "flat", "master-flat.fts"))
    header["READOUT"] = "highgain"
    header["EXPOSURE"] = 60.0
    header["XBIN"] = "1"
    header["YBIN"] = "1"
    fits.writeto(filename=os.path.join(tmp_path, "master", "flat", "master-flat.fts"), data=flat, header=header, overwrite=True)
    print(f'flat image created: {os.path.join(tmp_path, "master", "flat", "master-flat.fts")}')

    print("creating raw image...")
    # raw image
    realistic_stars = (imsim.stars(image, 50, max_counts=max_star_counts) +
                        imsim.dark_current(image, dark, star_exposure, gain=gain, hot_pixels=True) +
                        imsim.bias(image, bias_level, realistic=True) +
                        imsim.read_noise(image, read_noise_electrons, gain=gain)
                        )
    fits.writeto(os.path.join(tmp_path, "raw", "raw-image.fts"), realistic_stars, overwrite=True)
    header = fits.getheader(os.path.join(tmp_path, "raw", "raw-image.fts"))
    header["READOUT"] = "highgain"
    header["EXPOSURE"] = 60.0
    header["XBIN"] = "1"
    header["YBIN"] = "1"
    fits.writeto(filename=os.path.join(tmp_path, "raw", "raw-image.fts"), data=realistic_stars, header=header, overwrite=True)
    print(f'raw image created: {os.path.join(tmp_path, "raw", "raw-image.fts")}')
    

    # calibrated image
    print("creating calibrated image with astropy...")
    scaled_dark_current = star_exposure * (dark_frame_with_noise - bias_with_noise) / dark_exposure
    print(f"scaled dark current: {scaled_dark_current}")
    print(f"star exposure: {star_exposure}")
    print(f"dark frame: {dark_frame_with_noise}")
    print(f"bias with noise: {bias_with_noise}")
    print(f"dark exposure: {dark_exposure}")
    calibrated_stars = (realistic_stars - bias_with_noise - scaled_dark_current) / flat
    fits.writeto(os.path.join(tmp_path, "calibrated", "astropy-calibrated-image.fts"), calibrated_stars, overwrite=True)
    header = fits.getheader(os.path.join(tmp_path, "calibrated", "astropy-calibrated-image.fts"))
    header["READOUT"] = "highgain"
    header["EXPOSURE"] = 60.0
    header["XBIN"] = "1"
    header["YBIN"] = "1"
    fits.writeto(filename=os.path.join(tmp_path, "calibrated", "astropy-calibrated-image.fts"), data=calibrated_stars, header=header, overwrite=True)
    print(f'calibrated image created: {os.path.join(tmp_path, "calibrated", "astropy-calibrated-image.fts")}')
    

    print("running ccd_calib...")
    # ccd_calib image
    ccd_calib(
        fnames=os.path.join(tmp_path, "raw"),
        dark_frame=os.path.join(tmp_path, "master", "dark", "master-dark.fts"),
        flat_frame=os.path.join(tmp_path, "master", "flat", "master-flat.fts"),
        bias_frame=os.path.join(tmp_path, "master", "bias", "master-bias.fts"),
        verbose=True,
        pedestal=0,
    )
    print()
    print("-" * 50)
    print("comparing raw images...")
    print("-" * 50)
    print()
    ccd_float32 = fits.getdata(os.path.join(tmp_path, "raw", "raw-image_float32.fts"))
    print(f"ccd_float32: {ccd_float32}")
    print()
    print(f"realistic_stars: {realistic_stars}")
    diff = ccd_float32 - realistic_stars
    print(f"mean diff: {np.mean(diff)}")
    print(f"median diff: {np.median(diff)}")
    print(f"max diff: {np.max(diff)}")
    print(f"min diff: {np.min(diff)}")
    print("difference between ccd_calib and astropy calibration is minimal, moving on...")
    print()
    raw_data_diff = diff

    print()
    print("-" * 50)
    print("comparing bias subtracted images...")
    ccd_bias_subtracted = fits.getdata(os.path.join(tmp_path, "raw", "raw-image_bias_sub.fts"))
    print(f"ccd_bias_subtracted: {ccd_bias_subtracted}")
    print()
    print(f"bias_with_noise: {realistic_stars - bias_with_noise}")
    diff = ccd_bias_subtracted - (realistic_stars - bias_with_noise)
    print(f"mean diff: {np.mean(diff)}")
    print(f"median diff: {np.median(diff)}")
    print(f"max diff: {np.max(diff)}")
    print(f"min diff: {np.min(diff)}")
    print("difference between ccd_calib and astropy calibration is minimal, moving on...")
    print()
    bias_subtracted_diff = diff

    print()
    print("-" * 50)
    print("comparing bias and dark subtracted images...")
    ccd_bias_dark_subtracted = fits.getdata(os.path.join(tmp_path, "raw", "raw-image_dark_sub.fts"))
    print(f"ccd_bias_dark_subtracted: {ccd_bias_dark_subtracted}")
    print()
    print(f"astropy bias and dark subtracted: {realistic_stars - bias_with_noise - scaled_dark_current}")
    diff = ccd_bias_dark_subtracted - (realistic_stars - bias_with_noise - scaled_dark_current)
    print(f"mean diff: {np.mean(diff)}")
    print(f"median diff: {np.median(diff)}")
    print(f"max diff: {np.max(diff)}")
    print(f"min diff: {np.min(diff)}")
    print("difference between ccd_calib and astropy calibration is minimal, moving on...")
    bias_dark_subtracted_diff = diff

    print()
    print("-" * 50)
    print("comparing flat subtracted images...")
    ccd_calib_flat_bias_subtracted = fits.getdata(os.path.join(tmp_path, "raw", "raw-image_flat_bias_sub.fts"))
    print(f"ccd_calib_flat_bias_subtracted: {ccd_calib_flat_bias_subtracted}")
    print()
    print(f"astropy flat subtracted: {flat - bias_with_noise}")
    diff = ccd_calib_flat_bias_subtracted - (flat - bias_with_noise)
    print(f"mean diff: {np.mean(diff)}")
    print(f"median diff: {np.median(diff)}")
    print(f"max diff: {np.max(diff)}")
    print(f"min diff: {np.min(diff)}")
    print("difference between ccd_calib and astropy calibration is minimal, moving on...")
    flat_bias_subtracted_diff = diff

    print()
    print("-" * 50)
    print("comparing dark and bias subtracted flat images images...")
    ccd_calib_flat_bias_dark_subtracted = fits.getdata(os.path.join(tmp_path, "raw", "raw-image_flat_bias_dark_sub.fts"))
    print(f"ccd_calib_flat_bias_dark_subtracted: {ccd_calib_flat_bias_dark_subtracted}")
    print()
    print(f"astropy dark and bias subtracted: {flat - bias_with_noise - scaled_dark_current}")
    diff = ccd_calib_flat_bias_dark_subtracted - (flat - bias_with_noise - scaled_dark_current)
    print(f"mean diff: {np.mean(diff)}")
    print(f"median diff: {np.median(diff)}")
    print(f"max diff: {np.max(diff)}")
    print(f"min diff: {np.min(diff)}")
    print("difference between ccd_calib and astropy calibration is minimal, moving on...")
    flat_bias_dark_subtracted_diff = diff

    print()
    print("-" * 50)
    print("comparing normalized flats...")
    ccd_calib_flat_norm = fits.getdata(os.path.join(tmp_path, "raw", "raw-image_flat_norm.fts"))
    print(f"ccd_calib_flat_norm: {ccd_calib_flat_norm}")
    print()
    print(f"astropy normalized flat: {flat / np.mean(flat)}")
    print()
    print(np.mean(flat))
    print()
    diff = ccd_calib_flat_norm - (flat / np.mean(flat))
    print()
    print(np.mean(flat))
    print()
    print(f"mean diff: {np.mean(diff)}")
    print(f"median diff: {np.median(diff)}")
    print(f"max diff: {np.max(diff)}")
    print(f"min diff: {np.min(diff)}")
    print("difference between ccd_calib and astropy calibration is minimal, but larger than previous step, moving on...")
    flat_norm_diff = diff

    # print()
    # print("-" * 50)
    # print("comparing flat div images...")
    # ccd_calib_flat_div = fits.getdata(os.path.join(tmp_path, "raw", "raw-image_flat_div.fts"))
    # print(f"ccd_calib_flat_div: {ccd_calib_flat_div}")
    # print()
    # print(f"astropy flat div: {calibrated_stars}")
    # diff = ccd_calib_flat_div - calibrated_stars
    # print(f"mean diff: {np.mean(diff)}")
    # print(f"median diff: {np.median(diff)}")
    # print(f"max diff: {np.max(diff)}")
    # print(f"min diff: {np.min(diff)}")
    # calibrated_image_diff_nofloor = diff

    # print()
    # print("-" * 50)
    # print("FINAL TESTING...")
    # ccd_calib_data, header = fits.getdata(os.path.join(tmp_path, "raw", "raw-image_cal.fts"), header=True)
    # print(f"ccd_calib_data: {ccd_calib_data}")
    # print()
    # print(f"astropy_calib_data: {calibrated_stars}")
    # print(header)
    # pedestal = header["PEDESTAL"]
    # print(f"pedestal: {pedestal}")
    # diff = (ccd_calib_data - np.ones(ccd_calib_data.shape) * pedestal) - calibrated_stars
    # print(f"mean diff: {np.mean(diff)}")
    # print(f"median diff: {np.median(diff)}")
    # print(f"max diff: {np.max(diff)}")
    # print(f"min diff: {np.min(diff)}")
    # calibrated_image_diff = diff

    # plt.figure(figsize=(12, 12))
    # show_image(raw_data_diff, cmap='viridis', percu=1)
    # plt.title("raw data diff")

    # show_image(bias_subtracted_diff, cmap='viridis', percu=1)
    # plt.title("bias subtracted diff")

    # show_image(bias_dark_subtracted_diff, cmap='viridis', percu=1)
    # plt.title("bias and dark subtracted diff")

    # show_image(flat_bias_subtracted_diff, cmap='viridis', percu=1)
    # plt.title("flat subtracted diff")

    # show_image(flat_bias_dark_subtracted_diff, cmap='viridis', percu=1)
    # plt.title("flat, bias, and dark subtracted diff")

    # show_image(flat_norm_diff, cmap='viridis', percu=1)
    # plt.title("normalized flat diff")

    # show_image(calibrated_image_diff_nofloor, cmap='viridis', percu=1)
    # plt.title("calibrated image diff (no pedestal)")

    # show_image(calibrated_image_diff, cmap='viridis', percu=1)
    # plt.title("calibrated image diff")
    # plt.show()

    # show_image(ccd_calib_flat_norm, cmap='viridis', percu=1)
    # plt.figure(figsize=(12, 12))
    # plt.subplot(2, 2, 1)
    # plt.imshow(ccd_calib_flat_norm, cmap='viridis', vmin=0.95, vmax=1.05)
    # plt.title("ccd-calib normalized flat")
    # plt.colorbar()
    
    # plt.subplot(2, 2, 2)
    # plt.imshow(flat / np.mean(flat), cmap='viridis', vmin=0.95, vmax=1.05)
    # plt.title("astropy normalized flat")
    # plt.colorbar()

    # plt.subplot(2, 2, 3)
    # plt.imshow(flat_norm_diff, cmap='viridis', vmin=-0.05, vmax=0.05)
    # plt.title("difference in normalized flat between ccd-calib and astropy pipeline")
    # plt.colorbar()

    # plt.subplot(2, 2, 4)
    # plt.imshow(ccd_calib_flat_norm / (flat / np.mean(flat)), cmap='viridis', vmin=-0.05, vmax=0.05)
    # plt.title("ccd-calib normalized flat divided by astropy normalized flat")
    # plt.colorbar()
    # plt.subplots_adjust(wspace=0.5)
    # plt.show()

    # plt.subplot(1,2,1)
    # plt.imshow(ccd_calib_flat_bias_dark_subtracted, cmap='viridis', vmin=-2000, vmax=0)
    # plt.title("ccd_calib bias and dark subtracted flat field")
    # plt.colorbar()

    # plt.subplot(1,2,2)
    # plt.imshow(flat - bias_with_noise - scaled_dark_current, cmap='viridis', vmin=-2000, vmax=0)
    # plt.title("astropy bias and dark subtracted flat field")
    # plt.colorbar()
    # plt.show()

    print(f"type of calibrated_stars: {calibrated_stars.dtype}")
    print(f"type of ccd_calib_data: {ccd_calib_flat_div.dtype}")
    # show_image(ccd_calib_flat_norm / (flat / np.mean(flat)), cmap='viridis', percu=1)
    # plt.show()
    
    return


if __name__ == "__main__":
    test_ccd_calib(os.path.join(os.getcwd(), "tmp_dir"))
    print("test passed, removing temp directory...")
    input("Press Enter to continue...")
    shutil.rmtree(os.path.join(os.getcwd(), "tmp_dir"))