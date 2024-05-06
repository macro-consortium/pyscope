import glob
import logging
import os
import time
from pathlib import Path

import astroscrappy
import click
import numpy as np
from astropy.io import fits

logger = logging.getLogger(__name__)


@click.command(
    epilog="""Check out the documentation at
                https://pyscope.readthedocs.io/ for more
                information."""
)
@click.option(
    "-t",
    "--camera-type",
    type=click.Choice(["ccd", "cmos"]),
    default="ccd",
    show_choices=True,
    show_default=True,
    help="Camera type.",
)
@click.option(
    "-d",
    "--dark-frame",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to master dark frame. If camera type is CMOS, then the exposure time of the dark frame should match the exposure time of the target images.",
)
@click.option(
    "-b",
    "--bias-frame",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to master bias frame. Ignored if camera type is CMOS.",
)
@click.option(
    "-f",
    "--flat-frame",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to master flat frame. The script assumes the master flat frame has already been calibrated. The flat frame is normalized by the mean of the entire image before being applied to the target images.",
)
@click.option(
    "-s",
    "--astro-scrappy",
    nargs=2,
    default=(1, 3),
    show_default=True,
    help="Number of hot pixel removal iterations and estimated camera read noise in root-electrons per pixel per second.",
)
@click.option(
    "-c",
    "--bad-columns",
    default="",
    show_default=True,
    help="Comma-separated list of bad columns to fix by averaging the value of each pixel in the adjacent column.",
)
@click.option(
    "-i",
    "--in-place",
    is_flag=True,
    default=False,
    show_default=True,
    help="Overwrite input files.",
)
@click.option(
    "-p",
    "--pedestal",
    default=1000,
    show_default=True,
    help="Pedestal value to add to calibrated image.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    help="Print verbose output. Use multiple times for more verbosity.",
)
@click.argument("fnames", nargs=-1, type=click.Path(exists=True, resolve_path=True))
@click.version_option()
def ccd_calib_cli(
    fnames,
    dark_frame=None,
    bias_frame=None,
    flat_frame=None,
    camera_type="ccd",
    astro_scrappy=(1, 3),
    bad_columns="",
    in_place=False,
    verbose=0,
    pedestal=1000,
):
    """
    Calibrate CCD or CMOS images using master dark, bias, and flat frames. The calibrated images are saved
    with the suffix '_cal' appended to the original filename. This script may be used to pre-calibrate flats
    before combining them into a master flat frame. \b



    """
    if verbose == 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    logger.debug(
        f"""ccd_calib(\n\tcamera_type={camera_type}, \n\tdark_frame={dark_frame}, \n\tflat_frame={flat_frame}, \n\tbias_frame={bias_frame}, \n\tastro_scrappy={astro_scrappy}, \n\tbad_columns={bad_columns}, \n\tin_place={in_place}, \n\tfnames={fnames}, \n\tverbose={verbose}, \n\tpedestal={pedestal}\n)"""
    )

    logger.info("Loading calibration frames...")

    if camera_type == "ccd":
        if bias_frame is not None:
            logger.info(f"Loading bias frame: {bias_frame}")
            with fits.open(bias_frame) as hdul:
                bias = hdul[0].data
                bias_hdr = hdul[0].header
            bias = bias.astype(np.float64)

            try:
                bias_readout_mode = bias_hdr["READOUTM"]
            except KeyError:
                bias_readout_mode = bias_hdr["READOUT"]

            try:
                bias_exptime = round(bias_hdr["EXPTIME"], 3)
            except KeyError:
                bias_exptime = round(bias_hdr["EXPOSURE"], 3)

            try:
                bias_xbin = bias_hdr["XBINNING"]
            except:
                bias_xbin = bias_hdr["XBIN"]

            try:
                bias_ybin = bias_hdr["YBINNING"]
            except:
                bias_ybin = bias_hdr["YBIN"]

            logger.debug(f"Bias frame readout mode: {bias_readout_mode}")
            logger.debug(f"Bias frame exposure time: {bias_exptime}")
            logger.debug(f"Bias frame X binning: {bias_xbin}")
            logger.debug(f"Bias frame Y binning: {bias_ybin}")

    if dark_frame is not None:
        logger.info(f"Loading dark frame: {dark_frame}")
        with fits.open(dark_frame) as hdul:
            dark = hdul[0].data
            dark_hdr = hdul[0].header
        dark = dark.astype(np.float64)

        try:
            dark_readout_mode = dark_hdr["READOUTM"]
        except KeyError:
            dark_readout_mode = dark_hdr["READOUT"]

        try:
            dark_exptime = round(dark_hdr["EXPTIME"], 3)
        except KeyError:
            dark_exptime = round(dark_hdr["EXPOSURE"], 3)

        try:
            dark_xbin = dark_hdr["XBINNING"]
        except:
            dark_xbin = dark_hdr["XBIN"]

        try:
            dark_ybin = dark_hdr["YBINNING"]
        except:
            dark_ybin = dark_hdr["YBIN"]

        logger.debug(f"Dark frame readout mode: {dark_readout_mode}")
        logger.debug(f"Dark frame exposure time: {dark_exptime}")
        logger.debug(f"Dark frame X binning: {dark_xbin}")
        logger.debug(f"Dark frame Y binning: {dark_ybin}")

    if flat_frame is not None:
        logger.info(f"Loading flat frame: {flat_frame}")
        with fits.open(flat_frame) as hdul:
            flat = hdul[0].data
            flat_hdr = hdul[0].header

        flat = flat.astype(np.float64)

        try:
            flat_filter = flat_hdr["FILTER"]
        except KeyError:
            flat_filter = ""

        try:
            flat_readout_mode = flat_hdr["READOUTM"]
        except KeyError:
            flat_readout_mode = flat_hdr["READOUT"]

        try:
            flat_exptime = round(flat_hdr["EXPTIME"], 3)
        except KeyError:
            flat_exptime = round(flat_hdr["EXPOSURE"], 3)

        try:
            flat_xbin = flat_hdr["XBINNING"]
        except:
            flat_xbin = flat_hdr["XBIN"]

        try:
            flat_ybin = flat_hdr["YBINNING"]
        except:
            flat_ybin = flat_hdr["YBIN"]

        logger.debug(f"Flat frame readout mode: {flat_readout_mode}")
        logger.debug(f"Flat frame exposure time: {flat_exptime}")
        logger.debug(f"Flat frame X binning: {flat_xbin}")
        logger.debug(f"Flat frame Y binning: {flat_ybin}")

    for fname in fnames:
        logger.info(f"Calibrating {fname}...")
        image, hdr = fits.getdata(fname, header=True)

        image = image.astype(np.float64)

        try:
            image_filter = hdr["FILTER"]
        except KeyError:
            image_filter = ""

        try:
            image_readout_mode = hdr["READOUTM"]
        except KeyError:
            image_readout_mode = hdr["READOUT"]

        try:
            image_exptime = round(hdr["EXPTIME"], 3)
        except KeyError:
            image_exptime = round(hdr["EXPOSURE"], 3)

        try:
            image_xbin = hdr["XBINNING"]
        except:
            image_xbin = hdr["XBIN"]

        try:
            image_ybin = hdr["YBINNING"]
        except:
            image_ybin = hdr["YBIN"]

        logger.debug(f"Image readout mode: {image_readout_mode}")
        logger.debug(f"Image exposure time: {image_exptime}")
        logger.debug(f"Image X binning: {image_xbin}")
        logger.debug(f"Image Y binning: {image_ybin}")

        if dark_frame is not None:
            if image_readout_mode != dark_readout_mode:
                logger.warning(
                    f"Image readout mode ({image_readout_mode}) does not match dark readout mode ({dark_readout_mode})"
                )

            if image_xbin != dark_xbin:
                logger.warning(
                    f"Image X binning ({image_xbin}) does not match dark X binning ({dark_xbin})"
                )

            if image_ybin != dark_ybin:
                logger.warning(
                    f"Image Y binning ({image_ybin}) does not match dark Y binning ({dark_ybin})"
                )

        if flat_frame is not None:
            if image_readout_mode != flat_readout_mode:
                logger.warning(
                    f"Image readout mode ({image_readout_mode}) does not match flat readout mode ({flat_readout_mode})"
                )

            if image_xbin != flat_xbin:
                logger.warning(
                    f"Image X binning ({image_xbin}) does not match flat X binning ({flat_xbin})"
                )

            if image_ybin != flat_ybin:
                logger.warning(
                    f"Image Y binning ({image_ybin}) does not match flat Y binning ({flat_ybin})"
                )

            if image_filter != flat_filter:
                logger.warning(
                    f"Image filter ({image_filter}) does not match flat filter ({flat_filter})"
                )

        if camera_type == "cmos":
            if image_exptime != dark_exptime:
                logger.warning(
                    f"""Image exposure time ({image_exptime}) does not match dark exposure time ({dark_exptime}),
                    recommended for a CMOS camera"""
                )
            if flat_exptime != flat_dark_exptime:
                logger.warning(
                    f"""Flat exposure time ({flat_exptime}) does not match flat-dark exposure time ({flat_dark_exptime}),
                    recommended for a CMOS camera"""
                )

        hdr.add_comment(f"Calibrated using pyscope")
        hdr.add_comment(f"Calibration mode: {camera_type}")
        hdr.add_comment(f"Calibration dark frame: {dark_frame}")
        hdr.add_comment(f"Calibration flat frame: {flat_frame}")
        hdr.add_comment(f"Calibration bias frame: {bias_frame}")
        hdr.add_comment(f"Calibration astro-scrappy: {astro_scrappy}")
        hdr.add_comment(f"Calibration bad columns: {bad_columns}")

        cal_image = image.copy()

        if camera_type == "ccd":
            if bias_frame is not None:
                logger.info("Applying bias frame (CCD selected)...")
                cal_image -= bias

            if dark_frame is not None:
                logger.info(
                    """Applying the dark frame. CCD selected so a bias-subtracted
                            dark frame is scaled by the ratio of the image exposure time over
                            the dark exposure time then subtracted from the image."""
                )

                cal_image -= (dark - bias) * (image_exptime / dark_exptime)

        elif camera_type == "cmos":
            if dark_frame is not None:
                logger.info(
                    """Applying the dark frame. CMOS selected so a dark
                            is subtracted from the image with no bias and no exposure time scaling."""
                )
                cal_image -= dark

        if flat_frame is not None:
            logger.info("Checking if flat frame has a pedestal...")
            if "PEDESTAL" in flat_hdr:
                logger.info(f"Pedestal keyword found, value: {flat_hdr['PEDESTAL']}")
                flat_pedestal = flat_hdr["PEDESTAL"]
                logger.info(f"Subtracting pedestal of {flat_pedestal} from flat frame.")
                flat -= flat_pedestal

            logger.info("Normalizing the flat frame by the mean of the entire image.")
            flat_mean = np.mean(flat)
            logger.info(f"flat_mean: {flat_mean}")
            flat = np.divide(flat, flat_mean)

            logger.info("Applying the flat frame...")
            cal_image = np.divide(cal_image, flat)

        logger.info("Flooring the calibrated image...")
        cal_image = np.floor(cal_image)

        logger.info(f"Adding pedestal of {pedestal}")
        hdr["PEDESTAL"] = pedestal
        cal_image += pedestal

        if astro_scrappy[0] > 0:
            logger.info("Removing hot pixels...")
            t0 = time.time()
            mask, cal_image = astroscrappy.detect_cosmics(
                cal_image, niter=astro_scrappy[0], readnoise=astro_scrappy[1]
            )
            t = time.time() - t0
            hdr.add_comment(
                f"Removed hot pixels using astroscrappy, {astro_scrappy[0]} iterations"
            )
            hdr.add_comment("Hot pixel removal took %.1f seconds" % t)
            logger.debug(f"Hot pixel removal took {t} seconds")

        if len(bad_columns) > 0:
            logger.info("Fixing bad columns...")
            for badcol in bad_columns:
                cal_image[:, badcol] = (
                    cal_image[:, badcol - 1] + cal_image[:, badcol + 1]
                ) / 2

        logger.info("Clipping to uint16 range...")
        cal_image = np.clip(cal_image, 0, 65535)
        cal_image = cal_image.astype(np.uint16)

        logger.info("Writing calibrated status to header...")
        hdr["CALSTAT"] = True
        if in_place:
            logger.info(f"Overwriting {fname}")
            fits.writeto(fname, cal_image, hdr, overwrite=True)
        else:
            logger.info(f"Writing calibrated image to {fname}")
            fits.writeto(
                fname.split(".")[:-1][0] + "_cal.fts", cal_image, hdr, overwrite=True
            )

        logger.info("Done!")


ccd_calib = ccd_calib_cli.callback
